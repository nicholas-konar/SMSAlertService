from SMSAlertService import util, mongo, app
from SMSAlertService.user import User


class DAO:

    @staticmethod
    def set_cookie(user, cookie):
        info = f'Set cookie to user {user.username}.'
        error = f'Failed to set cookie for user {user.username}.'
        success = mongo.set_cookie(user.username, cookie).modified_count
        app.logger.info(info) if success else app.logger.error(error)
        return success

    @staticmethod
    def create_user(username, password, phonenumber):
        info = f'Created new account for user {username}.'
        error = f'Failed to create new account for user {username}.'
        acknowledged = mongo.create_user(username, password, phonenumber).acknowledged
        app.logger.info(info) if acknowledged else app.logger.error(error)
        return DAO.get_user_by_username(username)

    @staticmethod
    def verify_user(user):
        info = f'User {user.username}\'s phone number has been verified.'
        error = f'Failed to verify user {user.username} in the database. Current verified status: {user.verified}.'
        success = mongo.verify(user.username).modified_count
        app.logger.info(info) if success else app.logger.error(error)
        return success

    @staticmethod
    def block_user(user):
        info = f'User {user.username}\'s account has been blocked.'
        error = f'Failed to block user {user.username}\'s account. Current blocked status: {user.blocked}.'
        success = mongo.block(user.username).modified_count
        app.logger.info(info) if success else app.logger.error(error)
        return success

    @staticmethod
    def reset_password(user, new_password):
        info = f'Password reset successful for user {user.username}.'
        error = f'Failed to reset password for {user.username}.'
        success = mongo.reset_password(user.username, new_password).modified_count
        app.logger.info(info) if success else app.logger.error(error)
        return success


    @staticmethod
    def get_all_users():
        user_data = mongo.get_user_data()
        users = util.generate_users(user_data)
        return users

    @staticmethod
    def get_user_by_username(username):
        user_data = mongo.get_user_by_username(username)
        return None if user_data is None else User(user_data)

    @staticmethod
    def get_user_by_phonenumber(ph):
        user_data = mongo.get_user_by_phonenumber(ph)
        return None if user_data is None else User(user_data)

    @staticmethod
    def log_otp(user, message):
        # todo: iron this out
        app.logger.debug(f'OTP Data: {message}')
        # mongo.save_otp_data(user, otp)

    @staticmethod
    def add_keyword(user, keyword):
        if keyword not in user.keywords:
            info = f'User {user.username} added keyword {keyword}.'
            error = f'User {user.username} failed to add keyword {keyword}.'
            success = mongo.add_keyword(user.username, keyword).modified_count
            app.logger.info(info) if success else app.logger.error(error)
            return success
        else:
            return False

    @staticmethod
    def delete_keyword(user, keyword):
        info = f'User {user.username} deleted keyword {keyword}.'
        error = f'User {user.username} failed to delete keyword {keyword}.'
        success = mongo.delete_keyword(user.username, keyword).modified_count
        app.logger.info(info) if success else app.logger.error(error)
        return success

    @staticmethod
    def delete_all_keywords(user):
        info = f'User {user.username} deleted all keywords.'
        error = f'User {user.username} failed to delete all keywords.'
        success = mongo.delete_all_keywords(user.username).modified_count
        app.logger.info(info) if success else app.logger.error(error)
        return success


