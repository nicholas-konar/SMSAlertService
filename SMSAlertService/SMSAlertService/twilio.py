import configparser
import logging
import os

from twilio.rest import Client

from SMSAlertService import app

twilio_number = os.environ['TWILIO_NUMBER']
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
messaging_service_sid = os.environ['TWILIO_MESSAGING_SERVICE_SID']


def send(username, destination, link, keywords):
    client = Client(account_sid, auth_token)
    body = create_body(link, keywords)
    message = client.messages.create(
        body=body,
        messaging_service_sid=messaging_service_sid,
        to=destination
    )
    app.logger.debug(f'Message sent to {username} at: {destination} with SID: {message.sid}')
    return message


def create_body(link, keywords):
    formatted_keywords = format_keywords(keywords)
    subreddit = os.environ['REDDIT_SUBREDDIT']
    return f'A post on {subreddit} matched some of your keywords: {formatted_keywords}\n{link}'


def format_keywords(keywords):
    formatted_keywords = ''
    for keyword in keywords:
        formatted_keywords += ' ' + keyword
    return formatted_keywords

