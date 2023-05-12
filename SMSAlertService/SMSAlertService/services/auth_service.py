import secrets
import string
import bcrypt

from SMSAlertService import app
from SMSAlertService.resources.config import OTP_LENGTH


class AuthService:

    @staticmethod
    def generate_otp(length=OTP_LENGTH):
        otp = ''.join(secrets.choice(string.digits) for i in range(length))
        app.logger.debug(f"Generated OTP '{otp}'")
        return otp

    @staticmethod
    def authenticate_otp(expected, actual):
        return bcrypt.checkpw(actual.encode('utf-8'), expected)

    @staticmethod
    def hash_data(data):
        return bcrypt.hashpw(data.encode('utf-8'), bcrypt.gensalt(4))
