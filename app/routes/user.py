from .. import app, db
from flask import render_template, redirect, jsonify, url_for, request, session
from datetime import datetime
from flask_login import current_user
from .starling import Starling, exclude_from_auth_check
from ..models.user import load_user
from ..models.transaction import Transaction, Receipt
from ..models.estimate import Estimate
from ..forms.user import ReceiptForm
from werkzeug.exceptions import HTTPException
from ..models.asprise import Asprise



@app.context_processor
def flask_functions():
    """These functions are made available in HTML via Jinja2."""

    def pence_to_pounds(pence):
        return "£{:.2f}".format(pence / 100)
    
    return dict(datetime=datetime, pence_to_pounds=pence_to_pounds)


@app.route('/')
@exclude_from_auth_check
def home():
    """Redirect to the dashboard if the user is logged in, otherwise redirect to the login page."""

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))


@app.route('/dashboard/')
def dashboard():
    """The dashboard page."""

    if current_user.is_authenticated == False: return redirect('/login')
    
    name = session['name']
    
    return render_template('user/dashboard.html', title='Dashboard', name=name)


@app.route('/transaction_feed')
def transaction_feed():
    """Feeds transactions to the dashboard via htmx."""

    Starling.get_feed()

    user = load_user(current_user.id)
    transactions = db.paginate(user.transactions.order_by(db.desc('datetime')), per_page=6)

    return render_template('user/transaction_feed.html', transactions=transactions)


@app.route('/get-co2e-estimate/<transaction_id>')
def get_co2e_estimate(transaction_id):
    """Gets the CO2e estimate for a transaction."""

    transaction = Transaction.query.get(transaction_id)
    if transaction:
        estimate = Estimate(transaction)
        estimate.generate_estimate()

        return redirect(url_for('dashboard'))
        # return jsonify({'co2e': estimate.co2e, 'method': estimate.method})

    else: return 'not found', 404


@app.route('/add-receipt/<transaction_id>', methods=['GET', 'POST'])
def add_receipt(transaction_id):
    """Adds a receipt to a transaction."""

    receipt_form = ReceiptForm()

    if receipt_form.validate_on_submit():
        items_dict = {}
        for item in request.form.items():
            if item[0].startswith('i') and item[0][-1] != 'd':
                items_dict[item[1]] = request.form['p' + item[0][1:]]
        

        receipt = Receipt(
            transaction_id=transaction_id,
            items=items_dict
        )
        db.session.add(receipt)
        db.session.commit()
        return redirect(url_for('get_co2e_estimate', transaction_id=transaction_id))

    transaction = Transaction.query.get(transaction_id)
    if transaction:
        if not transaction.receipt.first():

            return render_template('user/receipt_form.html', receipt_form=receipt_form, transaction_id=transaction_id)
        
        else:
            return 'receipt already exists', 400


    else: return 'not found', 404


@app.route('/post-receipt/<transaction_id>', methods=['POST'])
def post_receipt(transaction_id):
    """Receieves a receipt, sends it to Asprise, and returns a html form containing the items to htmx."""

    if 'file' not in request.files:
        return 'no file', 400
    
    img = request.files['file']
    filename = img.filename

    # Asprise supports JPEG, PNG, TIFF, PDF
    if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.tiff') or filename.endswith('.pdf'):

        r = open('asprise-response.json', 'r').read() # Use to avoid maxing out the free limit on Asprise API calls in testing.
        # r = Asprise.get_receipt_data(img.read(), transaction_id)
        items = Asprise.extract_items_from_response(r)
        receipt_form = ReceiptForm()
        return render_template('user/auto-receipt_form.html', receipt_form=receipt_form, items=items, transaction_id=transaction_id), 200
    
    else:
        return 'invalid file type', 400
