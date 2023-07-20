from .. import app, db
from flask import render_template, redirect, jsonify, url_for
from datetime import datetime
from flask_login import current_user
from .starling import Starling
from ..models.user import load_user, Transaction, Receipt
from ..models.estimate import Estimate
from werkzeug.exceptions import HTTPException



@app.context_processor
def flask_functions():
    """These functions are made available in HTML via Jinja2."""

    def pence_to_pounds(pence):
        return "£{:.2f}".format(pence / 100)
    
    return dict(datetime=datetime, pence_to_pounds=pence_to_pounds)


@app.route('/')
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
    
    # If get_name fails, redirect to the Starling page to get a new access token.
    name = Starling.get_name()
    if name == None: return redirect(url_for('starling'))

    Starling.get_feed() # Update the database with the latest transactions.
    
    return render_template('user/dashboard.html', title='Dashboard', name=name)


@app.route('/transaction_feed')
def transaction_feed():
    """Feeds transactions to the dashboard via htmx."""

    user = load_user(current_user.id)
    transactions = db.paginate(user.transactions.order_by(db.desc('datetime')), per_page=6)

    return render_template('user/transaction_feed.html', transactions=transactions)


@app.route('/get-co2e-estimate/<transaction_id>')
def get_co2e_estimate(transaction_id):
    """Gets the CO2e estimate for a transaction."""

    transaction = Transaction.query.get(transaction_id)
    if transaction:
        estimate = Estimate(transaction)
        estimate.get_estimate()

        return jsonify({'co2e': estimate.co2e, 'method': estimate.method})

    else: return 'not found', 404


@app.route('/add-receipt/<transaction_id>')
def add_receipt(transaction_id):
    """Adds a receipt to a transaction."""

    transaction = Transaction.query.get(transaction_id)
    if transaction:
        if not transaction.receipt_id:
            receipt = Receipt(
                transaction_id=transaction_id,
                items={}
            )
            db.session.add(receipt)
            db.session.commit()

            return jsonify({'receipt_id': receipt.id})
        
        else:
            return 'receipt already exists', 400


    else: return 'not found', 404
