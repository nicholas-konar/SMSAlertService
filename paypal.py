import requests
import base64
import os

from SMSAlertService import app

client_id = os.environ['PAYPAL_CLIENT_ID']
client_secret = os.environ['PAYPAL_CLIENT_SECRET']


def get_access_token():
    app.logger.info('Fetching access token from paypal.')
    auth_string = f'{client_id}:{client_secret}'
    auth_string_encoded = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

    headers = {
        'Authorization': f'Basic {auth_string_encoded}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    payload = {
        'grant_type': 'client_credentials'
    }

    response = requests.post('https://api.paypal.com/v1/oauth2/token', headers=headers, data=payload)
    access_token = response.json()['access_token']
    return access_token


def get_order_details(access_token, order_id):
    app.logger.info(f'Fetching order {order_id} from paypal.')
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"https://api.paypal.com/v2/checkout/orders/{order_id}", headers=headers)
    return response.json()


def authenticate_order(order_details):
    return order_details.get('name') != 'RESOURCE_NOT_FOUND'
