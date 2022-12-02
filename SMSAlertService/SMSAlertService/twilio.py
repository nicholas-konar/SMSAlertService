import configparser
import logging
import os

from twilio.rest import Client

from SMSAlertService import app

config = configparser.RawConfigParser()
folder = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(folder, 'config.init')
config.read(file)

twilio_number = config.get('twilio', 'twilio_number')
account_sid = config.get('twilio', 'account_sid')
auth_token = config.get('twilio', 'auth_token')
messaging_service_sid = config.get('twilio', 'messaging_service_sid')


def send(username, destination, link, keywords):
    client = Client(account_sid, auth_token)
    body = create_body(link, keywords)
    message = client.messages.create(
        body=body,
        messaging_service_sid=messaging_service_sid,
        to=destination
    )
    app.logger.debug('Message sent to ' + username + ' at: ' + destination + ' with SID: ' + message.sid)


def create_body(link, keywords):
    formatted_keywords = format_keywords(keywords)
    subreddit = config.get('reddit', 'subreddit')
    return 'A post on ' + subreddit + ' matched some of your keywords: ' + formatted_keywords + '\n' + link


def format_keywords(keywords):
    formatted_keywords = ''
    for keyword in keywords:
        formatted_keywords += ' ' + keyword
    return formatted_keywords

