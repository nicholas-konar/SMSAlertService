import secrets
import string
import time

from SMSAlertService import app, twilio
from SMSAlertService.dao import DAO


class OtpService:

    @staticmethod
    def generate_otp():
        length = 6
        code = ''.join(secrets.choice(string.digits) for i in range(length))
        app.logger.info(f"Generated OTP '{code}'")
        return code

    @staticmethod
    def send_otp(otp, phonenumber):
        return twilio.send_otp(otp, phonenumber)

    @staticmethod
    def authenticate_otp(expected, actual):
        return True if expected == actual else False



