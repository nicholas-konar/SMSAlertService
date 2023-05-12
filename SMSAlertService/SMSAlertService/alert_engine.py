from SMSAlertService import reddit
from SMSAlertService.services import alert_service
from SMSAlertService.dao import DAO

dao = DAO()


def run():
    posts = reddit.get_new_posts()
    alerts = create_alerts_for_many(posts)
    alert_service.send_alerts(alerts)

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


