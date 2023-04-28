from SMSAlertService import mongo, reddit, twilio
from SMSAlertService.dao import DAO
from SMSAlertService.factories import alert_factory

dao = DAO()


def run():
    posts = reddit.get_new_posts()
    alerts = alert_factory.create_alerts_for_multiple_posts(posts)
    process_alerts(alerts)


def process_alerts(alerts):
    for alert in alerts:
        twilio.send_alert(alert)
        mongo.save_alert_data(alert)

