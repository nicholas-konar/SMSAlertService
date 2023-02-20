from SMSAlertService import util, mongo
from SMSAlertService.user import User


class DAO:

    def create_user(self, username, password, phonenumber):
        mongo.create_user(username, password, phonenumber)
        user_data = mongo.get_user_by_username(username)
        return User(user_data)

    def get_user_by_username(self, username):
        user_data = mongo.get_user_by_username(username)
        return User(user_data)

    def get_user_by_phonenumber(self, ph):
        user_data = mongo.get_user_by_phonenumber(ph)
        return User(user_data)

    def save_otp_data(self, user, otp):
        user.otps_sent += 1
        mongo.save_otp_data(user, otp)
