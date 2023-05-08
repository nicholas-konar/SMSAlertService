import requests
import base64
import os

from SMSAlertService import app

sandbox_client_id = os.environ['PAYPAL_SANDBOX_CLIENT_ID']
sandbox_client_secret = os.environ['PAYPAL_SANDBOX_CLIENT_SECRET']

client_id = os.environ['PAYPAL_CLIENT_ID']
client_secret = os.environ['PAYPAL_CLIENT_SECRET']


def get_access_token():
    app.logger.debug('Fetching access token from paypal.')
    auth_string = f'{sandbox_client_id}:{sandbox_client_secret}'
    auth_string_encoded = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

    headers = {
        'Authorization': f'Basic {auth_string_encoded}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    payload = {
        'grant_type': 'client_credentials'
    }

    response = requests.post('https://api.sandbox.paypal.com/v1/oauth2/token', headers=headers, data=payload)
    access_token = response.json()['access_token']
    return access_token
