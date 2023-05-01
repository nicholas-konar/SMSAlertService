import secrets
import string
import time

import bcrypt

from SMSAlertService import app, twilio, util
from SMSAlertService.dao import DAO


class OtpService:

    @staticmethod
    def generate_otp():
        length = 6
        code = ''.join(secrets.choice(string.digits) for i in range(length))
        app.logger.debug(f"Generated OTP '{code}'")
        return code

    @staticmethod
    def send_otp(phonenumber):
        otp = OtpService.generate_otp()
        # twilio.send_otp(otp, phonenumber)
        app.logger.debug('(Actual sending disabled in OTP Service)')
        return util.hash_data(otp)

    @staticmethod
    def authenticate_otp(expected, actual):
        return util.check_hash(data=actual, hashed_data=expected)



