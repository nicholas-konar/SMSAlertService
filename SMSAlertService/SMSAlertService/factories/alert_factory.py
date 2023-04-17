from SMSAlertService.alert import Alert
from SMSAlertService.dao import DAO


def create_alerts(posts):
    alerts = []
    for post in posts:
        batch = create_alert_batch_for_post(post)
        alerts.append(batch)
    return alerts


def create_alert_batch_for_post(post):
    dao = DAO()
    users = dao.get_all_users()
    batch = []
    for user in users:
        if user.requires_alert_for(post):
            alert = Alert(user, post.url, post.subreddit)
            batch.append(alert)
    return batch
