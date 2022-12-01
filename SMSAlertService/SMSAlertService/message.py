import configparser
import logging
import os

from twilio.rest import Client

from SMSAlertService import app

config = configparser.RawConfigParser()
thisfolder = os.path.dirname(os.path.abspath(__file__))
initfile = os.path.join(thisfolder, 'config.init')
config.read(initfile)
app.logger.debug(initfile)

twilio_number = config.get('twilio', 'twilio_number')
account_sid = config.get('twilio', 'account_sid')
auth_token = config.get('twilio', 'auth_token')
messaging_service_sid = config.get('twilio', 'messaging_service_sid')


def send(destination, link, keywords):
    client = Client(account_sid, auth_token)
    body = create_body(link, keywords)
    message = client.messages.create(
        body=body,
        messaging_service_sid=messaging_service_sid,
        to=destination
    )
    app.logger.debug('Message sent to ' + destination + ' with SID: ' + message.sid)


def create_body(link, keywords):
    formatted_keywords = format_keywords(keywords)
    return 'There\'s a new post on GAFS that matched some of your keywords: ' + formatted_keywords + '\n' + link


def format_keywords(keywords):
    formatted_keywords = ''
    for keyword in keywords:
        formatted_keywords += ' ' + keyword
    return formatted_keywords

