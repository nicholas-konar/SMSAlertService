from SMSAlertService.alert import Alert
from SMSAlertService.dao import DAO

dao = DAO()


# multi sub support:
# from array of posts, return array of alerts

def get_alerts(posts):
    alerts = []
    for post in posts:
        batch = create_alert_batch_for_post(post)
        alerts.append(batch)
    return alerts


def create_alert_batch_for_post(post):
    users = dao.get_all_users()
    batch = []
    for user in users:
        if user.requires_alert_for(post):
            alert = Alert(user, post.url, post.subreddit)
            batch.append(alert)
    return batch
