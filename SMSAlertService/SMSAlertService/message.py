import logging

from twilio.rest import Client

twilio_number = '+12163508050'
account_sid = 'AC861b4f8f25965d16957760151a510667'
auth_token = '090c9846b50ac44150266671017b4c67'


def send(destination, link, keywords):
    client = Client(account_sid, auth_token)
    body = create_body(link, keywords)
    message = client.messages.create(
        body=body,
        messaging_service_sid='MGca7ef8a1981f4ae814dc3a60fe0caa15',
        to=destination
    )
    log = logging.getLogger('GAFSAlertService')
    log.info('Message sent to ' + destination + ' with SID: ' + message.sid)


def format_keywords(keywords):
    formatted_keywords = ''
    for keyword in keywords:
        formatted_keywords += ' ' + keyword
    return formatted_keywords


def create_body(link, keywords):
    formatted_keywords = format_keywords(keywords)
    return 'There\'s a new post on GAFS that matched some of your keywords: ' + formatted_keywords + '\n' + link


