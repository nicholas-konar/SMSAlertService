from SMSAlertService import twilio
from SMSAlertService.resources.sms_templates import ORDER_CONFIRMATION_MSG, STANDARD_ALERT_MSG, OTP_MSG
from SMSAlertService.services.auth_service import AuthService


class AlertService:

    @staticmethod
    def send_alerts(alerts):
        for alert in alerts:
            body = STANDARD_ALERT_MSG.format(
                subreddit=alert.subreddit,
                keywords=alert.keywords_found,
                url=alert.url
            )
            twilio.send_message(body=body, ph=alert.owner.phonenumber)
            # mongo.save_alert_data(alert)


    @staticmethod
    def send_otp(phonenumber):
        otp = AuthService.generate_otp()
        body = OTP_MSG.format(otp=otp)
        twilio.send_message(body=body, ph=phonenumber)
        return AuthService.hash_data(otp)


    @staticmethod
    def send_order_confirmation(user, order_description):
        body = ORDER_CONFIRMATION_MSG.format(order_description=order_description)
        twilio.send_message(body=body, ph=user.phonenumber)


    @staticmethod
    def send_admin(body):
        twilio.send_message(body=body, admin=True)
