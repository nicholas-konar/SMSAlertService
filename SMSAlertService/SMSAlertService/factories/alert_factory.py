from SMSAlertService.alert import Alert
from SMSAlertService.dao import DAO


def create_alerts_for_multiple_posts(posts):
    alerts = []
    for post in posts:
        batch = create_alerts_for_single_post(post)
        for alert in batch:
            alerts.append(alert)
    return alerts


def create_alerts_for_single_post(post):
    dao = DAO()
    users = dao.get_all_users()
    batch = []
    for user in users:
        if user.requires_alert_for_post(post):
            alert = Alert(user, post)
            batch.append(alert)
    return batch
