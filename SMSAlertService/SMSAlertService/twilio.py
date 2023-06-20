import os

from twilio.rest import Client
from SMSAlertService import app

twilio_number = os.environ['TWILIO_NUMBER']
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
messaging_service_sid = os.environ['TWILIO_MESSAGING_SERVICE_SID']


def send_message(body: str, ph=None, admin: bool = False):
    client = Client(account_sid, auth_token)
    destination = os.environ['ADMIN_NUMBER'] if admin else ph
    message = client.messages.create(
        body=body,
        messaging_service_sid=messaging_service_sid,
        to=destination
    )
    # message = None
    # app.logger.debug(f'Sent pretend message to {destination}. Admin = {admin} Body = {body}')
    return message
