from SMSAlertService import twilio, mongo
from SMSAlertService.alert import Alert
from SMSAlertService.dao import DAO
from twilio.base.exceptions import TwilioRestException

from SMSAlertService.resources import sms_templates
from SMSAlertService.resources.sms_templates import ORDER_COMPLETE_MSG


def process_alerts(alerts):
    for alert in alerts:
        twilio.send_alert(alert)
        mongo.save_alert_data(alert)


def create_alerts_for_many(posts):
    alerts = []
    users = DAO.get_all_users()
    for post in posts:
        batch = create_alerts_for_one(post, users)
        alerts.extend(batch)
    return alerts


def create_alerts_for_one(post, users):
    batch = []
    for user in users:
        if user.requires_alert_for_post(post):
            alert = Alert(user, post)
            batch.append(alert)
    return batch


def send_order_fulfilled_msg(user, order_description):
    try:
        body = ORDER_COMPLETE_MSG.format(order_description=order_description)
        twilio.send_message(body=body, ph=user.phonenumber)
    except TwilioRestException as e:
        body = f'TwilioRestException during order fulfillment notification for {user.username}.\n{e.details}'
        twilio.send_message(body=body, admin=True)


def alert_admin(body):
    twilio.send_message(body=body, admin=True)