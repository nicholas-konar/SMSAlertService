from SMSAlertService import util, mongo, app
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

    @staticmethod
    def add_keyword(user, keyword):
        if keyword not in user.keywords:
            info = f'User {user.username} added keyword {keyword}.'
            error = f'User {user.username} failed to add keyword {keyword}.'
            success = mongo.add_keyword(user.username, keyword).modified_count
            app.logger.info(info) if success else app.logger.error(error)
            return success

    @staticmethod
    def delete_keyword(user, keyword):
        info = f'User {user.username} deleted keyword {keyword}.'
        error = f'User {user.username} failed to delete keyword {keyword}.'
        success = mongo.delete_keyword(user.username, keyword).modified_count
        app.logger.info(info) if success else app.logger.error(error)
        return success

    @staticmethod
    def delete_all_keywords(user):
        mongo.delete_all_keywords(user.username)

