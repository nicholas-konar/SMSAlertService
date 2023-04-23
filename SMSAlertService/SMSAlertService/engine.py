from SMSAlertService import mongo, reddit, twilio
from SMSAlertService.dao import DAO
from SMSAlertService.factories import alert_factory
from SMSAlertService.otp import Otp

dao = DAO()


def run():
    posts = reddit.get_latest_posts()
    alerts = alert_factory.create_alerts(posts)
    process_alerts(alerts)


def process_alerts(alerts):
    for alert in alerts:
        twilio.send_alert(alert)
        mongo.save_alert_data(alert)


def process_otp(user):
    otp = Otp(user.phonenumber)
    twilio.send_otp(otp)
    dao.record_otp_data(user, otp)
    if user.otps_sent >= 4:
        mongo.block(user)  # block but still send the 5th OTP

