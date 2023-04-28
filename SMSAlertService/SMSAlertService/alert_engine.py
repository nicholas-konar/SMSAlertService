from SMSAlertService import mongo, reddit, twilio
from SMSAlertService.dao import DAO
from SMSAlertService.services import alert_service

dao = DAO()


def run():
    posts = reddit.get_new_posts()
    alerts = alert_service.create_alerts_for_many(posts)
    alert_service.send(alerts)

