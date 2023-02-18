import os

from SMSAlertService import mongo, reddit, twilio, util
from SMSAlertService.alert import Alert
from SMSAlertService.otp import Otp

subreddit = os.environ['REDDIT_SUBREDDIT']


def run():
    post = reddit.new_post()
    if post:
        alerts = []
        users = mongo.get_users()
        for user in users:
            matching_keywords = []
            for keyword in user['Keywords']:
                if util.keyword_match(user, keyword, post):
                    matching_keywords.append(keyword)
            if matching_keywords and int(user['Units']) > 0 and not mongo.blacklisted(user):
                alert = Alert(user, post.url, matching_keywords, subreddit)
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
