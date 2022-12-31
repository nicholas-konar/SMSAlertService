import os
from twilio.rest import Client
from SMSAlertService import app

twilio_number = os.environ['TWILIO_NUMBER']
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
messaging_service_sid = os.environ['TWILIO_MESSAGING_SERVICE_SID']


def send_alert(username, destination, link, keywords):
    client = Client(account_sid, auth_token)
    body = build_alert_body(link, keywords)
    message = client.messages.create(
        body=body,
        messaging_service_sid=messaging_service_sid,
        to=destination
    )
    app.logger.debug(f'Message sent to {username} at: {destination} with SID: {message.sid}')
    return message


def send_otp(destination, otp):
    client = Client(account_sid, auth_token)
    body = build_otp_body(otp)
    message = client.messages.create(
        body=body,
        messaging_service_sid=messaging_service_sid,
        to=destination
    )
    app.logger.debug(f'OTP sent to {destination} with SID: {message.sid}')
    return message


def build_alert_body(link, keywords):
    formatted_keywords = format_keywords(keywords)
    subreddit = os.environ['REDDIT_SUBREDDIT']
    return f'www.smsalertservice.com\n\nA post on {subreddit} matched the following keywords: {formatted_keywords}\n{link}'


def build_otp_body(otp):
    return f'SMS Alert Service: Your one time password is {otp}.\nwww.smsalertservice.com'


def format_keywords(keywords):
    formatted_keywords = ''
    for keyword in keywords:
        formatted_keywords += ' ' + keyword
    return formatted_keywords
