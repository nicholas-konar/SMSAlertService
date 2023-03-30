import os

from SMSAlertService import mongo, reddit, twilio, util
from SMSAlertService.alert import Alert
from SMSAlertService.dao import DAO
from SMSAlertService.otp import Otp

subreddit = os.environ['REDDIT_SUBREDDIT']

dao = DAO()

# test for merge

def run():
    if post := reddit.new_post():
        alerts = create_alerts(post) # todo: build alert factory
        process_alerts(alerts)

        
def create_alerts(post):
    users = dao.get_all_users()
    alerts = []
    for user in users:
        if user.requires_alert_for(post):
            alert = Alert(user, post.url, subreddit)
            alerts.append(alert)
    return alerts


def process_alerts(alerts):
    for alert in alerts:
        twilio.send_alert(alert)
        mongo.save_alert_data(alert)


def process_otp(user):
    if user.otps_sent < 5:
        otp = Otp(user.phonenumber)
        twilio.send_otp(otp)
        dao.save_otp_data(user, otp)
    else:
        mongo.block(user)
