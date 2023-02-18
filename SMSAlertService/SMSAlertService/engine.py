import os

from SMSAlertService import mongo, reddit, twilio, util
from SMSAlertService.alert import Alert
from SMSAlertService.otp import Otp

subreddit = os.environ['REDDIT_SUBREDDIT']


def run():
    post = reddit.new_post()
    if post:
        user_data_set = mongo.get_user_data()
        users = util.generate_users(user_data_set)
        alerts = []

        for user in users:
            if user.requires_alert_for(post):
                alert = Alert(user, post.url, subreddit)
                alerts.append(alert)

        process_alerts(alerts)


def process_alerts(alerts):
    for alert in alerts:
        twilio.send_alert(alert)
        mongo.save_alert_data(alert)


def process_otp(ph):
    otp = Otp(ph)
    twilio.send_otp(otp)
    mongo.save_otp_data(otp)
