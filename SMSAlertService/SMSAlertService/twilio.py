import os
from twilio.rest import Client
from SMSAlertService import app, util

twilio_number = os.environ['TWILIO_NUMBER']
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
messaging_service_sid = os.environ['TWILIO_MESSAGING_SERVICE_SID']


def send_alert(username, destination, link, keywords, units):
    client = Client(account_sid, auth_token)
    body = build_alert_body(link, keywords, units)
    message = client.messages.create(
        body=body,
        messaging_service_sid=messaging_service_sid,
        to=destination
    )
    app.logger.info(f'Message sent to {username} at: {destination} with SID: {message.sid}')
    return message


def build_alert_body(link, keywords, units):
    formatted_keywords = util.format_keywords(keywords)
    subreddit = os.environ['REDDIT_SUBREDDIT']
    if units == 0:
        return f'You\'re out of alerts! Reload at www.smsalertservice.com/profile' \
               f'\n\nA post on {subreddit} matched the following keywords: {formatted_keywords}\n{link}'
    elif units < 5:
        return f'Heads up: You only have {units} alert(s) left! Reload at www.smsalertservice.com/profile\n\n' \
               f'A post on {subreddit} matched the following keywords: {formatted_keywords}\n{link}'
    else:
        return f'www.smsalertservice.com\n\nA post on {subreddit} matched the following keywords: {formatted_keywords}\n{link}'


def send_otp(destination, otp):
    client = Client(account_sid, auth_token)
    body = build_otp_body(otp)
    message = client.messages.create(
        body=body,
        messaging_service_sid=messaging_service_sid,
        to=destination
    )
    app.logger.info(f'OTP sent to {destination} with SID: {message.sid}')
    return message


def build_otp_body(otp):
    return f'Your verification code is {otp}.\nwww.smsalertservice.com'


