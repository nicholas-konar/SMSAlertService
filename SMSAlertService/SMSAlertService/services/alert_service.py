from SMSAlertService import twilio, mongo
from SMSAlertService.alert import Alert
from SMSAlertService.dao import DAO


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
