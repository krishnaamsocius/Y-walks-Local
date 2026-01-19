

from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
import json
import secrets

def generate_token(length=32):
    # Generate a random token with the specified length
    token = secrets.token_hex(length)
    return token

def is_session_token_expired(session):
    # Get the token expiration time from the session
    expiration = session.get('token_expiration')

    # Check if the expiration time exists and if it is in the past
    if expiration and datetime.now() > expiration:
        return True  # Token has expired
    else:
        return False  # Token is still valid


class MobileController(http.Controller):

    @http.route('/api/authenticate', type='json', auth='none', methods=['POST'], csrf=False,cors='*')
    def mobile_login(self, **kwargs):
        # Retrieve the login credentials from the request
        username = request.jsonrequest.get('username')
        password = request.jsonrequest.get('password')

        # Authenticate with the Odoo server and obtain a session ID
        uid = request.session.authenticate(request.db, username, password)
        if uid is not False:
            # Generate a unique token for the authenticated user
            token = generate_token()
            expiration = datetime.now() + timedelta(hours=2)  # Set token expiration to 2 hours

            # Store the token and expiration in the user session
            session = request.session
            session['token'] = token
            session['token_expiration'] = expiration
            print("sess", session)
            session_id = request.session.get('token')
            response = {
                'session_id': session_id,
                'uid': request.session.uid,
                'message': 'Login successful',
            }
        else:
            response = {
                'message': 'Login failed',
            }

        return response
        # return json.dumps(response)


    @http.route('/api/v1/auth', type='http', auth='user', methods=['GET'])
    def get_sale_orders(self, **kw):
        return True