import os

from twilio.rest import Client

from SMSAlertService import application

twilio_number = os.getenv('twilio_number')
account_sid = os.getenv('twilio_account_sid')
auth_token = os.getenv('twilio_auth_token')
messaging_service_sid = os.getenv('twilio_messaging_service_sid')


def send(username, destination, link, keywords):
    client = Client(account_sid, auth_token)
    body = create_body(link, keywords)
    message = client.messages.create(
        body=body,
        messaging_service_sid=messaging_service_sid,
        to=destination
    )
    application.logger.debug(f'Message sent to {username} at: {destination} with SID: {message.sid}')
    return message


def create_body(link, keywords):
    formatted_keywords = format_keywords(keywords)
    subreddit = os.environ['reddit_subreddit']
    return f'A post on {subreddit} matched some of your keywords: {formatted_keywords}\n{link}'


def format_keywords(keywords):
    formatted_keywords = ''
    for keyword in keywords:
        formatted_keywords += ' ' + keyword
    return formatted_keywords

