from SMSAlertService import util, mongo
from SMSAlertService.user import User


class DAO:

    @staticmethod
    def create_user(username, password, phonenumber):
        mongo.create_user(username, password, phonenumber)
        user_data = mongo.get_user_by_username(username)
        return User(user_data)

    @staticmethod
    def get_all_users():
        user_data = mongo.get_user_data()
        users = util.generate_users(user_data)
        return users

    @staticmethod
    def get_user_by_username(username):
        user_data = mongo.get_user_by_username(username)
        return User(user_data)

    @staticmethod
    def get_user_by_phonenumber(ph):
        user_data = mongo.get_user_by_phonenumber(ph)
        return User(user_data)

    @staticmethod
    def record_otp_data(user, otp):
        user.otps_sent += 1
        mongo.save_otp_data(user, otp)
