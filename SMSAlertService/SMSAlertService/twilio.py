import os
from twilio.rest import Client
from SMSAlertService import app, util

twilio_number = os.environ['TWILIO_NUMBER']
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
messaging_service_sid = os.environ['TWILIO_MESSAGING_SERVICE_SID']


def send_alert(alert):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=alert.body,
        messaging_service_sid=messaging_service_sid,
        to=alert.destination
    )
    app.logger.info(f'Message sent to {alert.owner} at: {alert.destination} with SID: {message.sid}')
    return message


def send_otp(otp):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=otp.body,
        messaging_service_sid=messaging_service_sid,
        to=otp.destination
    )
    app.logger.info(f'OTP sent to {otp.destination} with SID: {message.sid}')
    return message


def build_otp_body(otp):
    return f'Your verification code is {otp}.\nwww.smsalertservice.com'
