from .. import app, db
from flask import session, url_for, redirect, jsonify
from flask_login import current_user, login_required
from authlib.integrations.requests_client import OAuth2Session
from flask import make_response, redirect, request
from ..models.user import load_user
from ..models.transaction import FeedLog, Transaction, Merchant
import os, requests, json
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import text


# Variables for requests to Starling's API.
client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
auth_uri = 'https://oauth-sandbox.starlingbank.com'
api_uri = 'https://api-sandbox.starlingbank.com'
user_agent = 'GroceryEmissionTracker|SmithJJ7@cardiff.ac.uk|FlaskApp|1.0'
acceptable_categories = ['GROCERIES', 'EATING_OUT']



@app.before_request
def check_authorized():
    """Checks that the user is authorised with Starling and that some basic account info is available."""

    if request.endpoint in app.view_functions and not hasattr(app.view_functions[request.endpoint], 'exclude_from_auth_check') and current_user.is_authenticated:

        if 'access_token' not in session: return redirect(url_for('get_access_token'))
        else:
            # Get name is used to check for an expired access token.
            name = Starling.get_name()
            if name is None: return redirect(url_for('get_access_token'))
            else: session['name'] = name

            # If there is an access token the following required data should be available, but check.
        if 'account_uid' not in session or 'default_category' not in session:
            r = Starling.get_account_info()
            if 'error' in r and r['error'] == 'invalid_token': return redirect(url_for('get_access_token'))


def exclude_from_auth_check(func):
    """Decorator to exclude a route from the check_authorized function."""

    func.exclude_from_auth_check = True
    return func
    



class Starling:
    """A class for interacting with Starling's API."""

    @staticmethod
    def get_name() -> str or None:
        """Requests an account holder's name from Starling's API. Returns the name if available, else None."""

        access_token = session['access_token']
        headers = {'Authorization': f'Bearer {access_token}', 'user_agent': user_agent}
        url = api_uri + '/api/v2/account-holder/name'
        r = requests.get(url, headers=headers)
        dict = json.loads(r.text)

        if 'accountHolderName' in dict: return dict['accountHolderName']
    
    @staticmethod
    def get_account_info():
        """Requests account information from Starling's API. Returns a dictionary of info if available, else None."""

        access_token = session['access_token']
        url = api_uri + '/api/v2/accounts'
        headers = {'Authorization': f'Bearer {access_token}', 'user_agent': user_agent}
        r = requests.get(url, headers=headers)
        dict = json.loads(r.text)

        session['account_uid'] = dict['accounts'][0]['accountUid']
        session['default_category'] = dict['accounts'][0]['defaultCategory']

        return dict

    @staticmethod
    def logout():
        """Tells Starling to invalidate the current access token, forcing re-authentication before further use."""

        access_token = session['access_token']
        headers = {'Authorization': f'Bearer {access_token}', 'user_agent': user_agent}
        url = api_uri + '/api/v2/identity/logout'
        requests.put(url, headers=headers)
    
    @staticmethod
    def get_feed() -> dict or None:
        """Requests the user's feed from Starling's API. Returns a dictionary of feed items if available, else None."""

        # Load user, get last pull datetime, and get account info.
        user = load_user(current_user.id)
        feed_logs = user.feed_logs
        
        if feed_logs.all(): last_pull = feed_logs.order_by(text('datetime desc')).limit(1).first().datetime
        else: last_pull = datetime.utcnow() - timedelta(days=7)

        last_pull = last_pull.isoformat(timespec='milliseconds') + 'Z'

        account_uid = session['account_uid']
        default_category = session['default_category']
        access_token = session['access_token']

        # Get the transactions.
        url = f'{api_uri}/api/v2/feed/account/{account_uid}/category/{default_category}?changesSince={last_pull}'
        headers = {'Authorization': f'Bearer {access_token}', 'user_agent': user_agent}
        r = requests.get(url, headers=headers)
        current_datetime = datetime.utcnow()
        dict = json.loads(r.text)

        # Check if there are acceptable feed items, if so count them, add to DB, and log.
        feed_id = str(uuid4())
        count = 0

        # if 'feedItems' not in dict: return None
        for item in dict['feedItems']:
            item_id = item['feedItemUid']
            if item['spendingCategory'] in acceptable_categories and Transaction.query.get(item_id) == None:

                # Add the merchant to the DB if it doesn't already exist.
                if Merchant.query.get(item['counterPartyUid']) == None:
                    merchant = Merchant(
                        id=item['counterPartyUid'],
                        name=item['counterPartyName'],
                        mcc=Starling.get_mcc(item_id)
                    )
                    db.session.add(merchant)
                    db.session.commit()

                # Add the transaction to the DB.
                item['feedItemUid'] = Transaction(
                    id=item['feedItemUid'],
                    amount_pence=item['amount']['minorUnits'],
                    datetime=datetime.fromisoformat(item['transactionTime'][:-1]),
                    user_id=user.id,
                    feed_log_id=feed_id,
                    merchant_id=item['counterPartyUid']
                )
                db.session.add(item['feedItemUid'])
                count += 1
            
        # Commit the changes to the DB and log the feed pull.
        if count > 0:
            new_feed_log = FeedLog(
                id=feed_id,
                user_id=user.id,
                datetime=current_datetime,
                item_count=count
            )
            db.session.add(new_feed_log)
            db.session.commit()

    @staticmethod
    def get_mcc(feed_item_uid: uuid4) -> dict or None:
        """Requests the merchant data for a given feed item from Starling's API. Returns a dictionary of data if available, else None."""

        account_uid = session["account_uid"]
        default_category = session["default_category"]
        access_token = session['access_token']

        # Get the merchant data.
        uri = f'{api_uri}/api/v2/feed/account/{account_uid}/category/{default_category}/{feed_item_uid}/mastercard'
        headers = {'Authorization': f'Bearer {access_token}', 'user_agent': user_agent}
        r = requests.get(uri, headers=headers)
        if 'mcc' in r.text:
            return json.loads(r.text)['mcc']



@app.route('/starling')
@login_required
@exclude_from_auth_check
def get_access_token():
    """Requests an access token from Starling's API."""

    # Set up an OAuth session.
    client = OAuth2Session(client_id, client_secret)
    user = load_user(current_user.id)

    # First try fetching a refresh token from the database and using it to get a new access token.
    try:

        token = client.refresh_token(f'{api_uri}/oauth/access-token', refresh_token=user.refresh_token, client_id=client_id, client_secret=client_secret)
        session['access_token'] = token['access_token']

        # Update refresh token in the database.
        user.refresh_token = (f'{token["refresh_token"]}')
        user.refresh_token_date = datetime.now()
        db.session.commit()

        return redirect(url_for('home'))
    
    except:

        uri, state = client.create_authorization_url(auth_uri)

        # Response and cookies.
        resp = make_response(redirect(uri))
        resp.set_cookie(
            'state',
            value=f'{state}',
            # secure=True,
            httponly=True,
            samesite='Strict'
            )
    
        return resp



@app.route('/authorize')
@login_required
@exclude_from_auth_check
def authorize():
    """Authorise Starling API connection once returned from their external OAuth login."""

    # Session must be reinstated after being redirected to Starling
    cookies = request.cookies
    state = cookies.get('state')
    client = OAuth2Session(client_id, client_secret, state=state)

    # Get the access token. The fetch token method will automatically check the state in case of CSRF attack
    authorization_response = request.url
    token = client.fetch_token(f'{api_uri}/oauth/access-token', authorization_response=authorization_response, client_id=client_id, client_secret=client_secret)

    # Response, state cookie, and access token cookie.
    resp = make_response(redirect('/dashboard'))
    resp.set_cookie(
        'state',
        expires=0
        )
    session['access_token'] = token['access_token']

    # Update the refresh token in the database.
    user = load_user(current_user.id)
    user.refresh_token = token["refresh_token"]
    user.refresh_token_date = datetime.now()
    
    # If there's no account holder uid on record then pull one and save it to the DB.
    if user.starling_uid == None:
        headers = {'Authorization': f'Bearer {token["access_token"]}', 'user_agent': user_agent}
        url = f'{api_uri}/api/v2/account-holder'
        r = requests.get(url, headers=headers)
        data = r.json()
        starling_uid = data['accountHolderUid']
        user.starling_uid = starling_uid
    
    db.session.commit()

    return resp
