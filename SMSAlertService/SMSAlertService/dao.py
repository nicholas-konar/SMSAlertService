from SMSAlertService import util, mongo, app
from SMSAlertService.user import User


class DAO:

    @staticmethod
    def create_account(username, password, phonenumber, verified, cookie):
        timestamp = util.timestamp()
        pw_hash = util.hash_data(password)
        insertion = mongo.create_user(username=username,
                                      pw_hash=pw_hash,
                                      phonenumber=phonenumber,
                                      verified=verified,
                                      timestamp=timestamp,
                                      cookie=cookie)
        info = f'Created new account for {username}.'
        error = f'Failed to create new account for {username}.'
        app.logger.info(info) if insertion.acknowledged else app.logger.error(error)
        return insertion

    @staticmethod
    def set_cookie(user, cookie):
        success = mongo.set_cookie(user.id, cookie).modified_count
        info = f'Set cookie for user {user.username}.'
        error = f'Failed to set cookie for user {user.username}.'
        app.logger.info(info) if success else app.logger.error(error)
        return success

    @staticmethod
    def get_all_active_users():
        user_data_set = mongo.get_all_active_user_data()
        return [User(user_data) for user_data in user_data_set]

    @staticmethod
    def get_user_by_id(user_id):
        user_data = mongo.get_user_data_by_id(user_id)
        return None if user_data is None else User(user_data)

    @staticmethod
    def get_user_by_username(username):
        user_data = mongo.get_user_data_by_username(username)
        return None if user_data is None else User(user_data)

    @staticmethod
    def get_user_by_phonenumber(ph):
        user_data = mongo.get_user_data_by_phonenumber(ph)
        return None if user_data is None else User(user_data)

    @staticmethod
    def add_keyword(user, keyword):
        if keyword in user.keywords:
            return False
        success = mongo.add_keyword(user.id, keyword).modified_count
        info = f'{user.username} added keyword {keyword}.'
        error = f'{user.username} failed to add keyword {keyword}.'
        app.logger.info(info) if success else app.logger.error(error)
        return success

    @staticmethod
    def delete_keyword(user, keyword):
        success = mongo.delete_keyword(user.id, keyword).modified_count
        info = f'{user.username} deleted keyword {keyword}.'
        error = f'{user.username} failed to delete keyword {keyword}.'
        app.logger.info(info) if success else app.logger.error(error)
        return success

    @staticmethod
    def delete_all_keywords(user):
        success = mongo.delete_all_keywords(user.username).modified_count
        info = f'{user.username} deleted all keywords.'
        error = f'{user.username} failed to delete all keywords.'
        app.logger.info(info) if success else app.logger.error(error)
        return success

    @staticmethod
    def block_user(user):
        success = mongo.block(user.id).modified_count
        info = f'{user.username}\'s account has been blocked.'
        error = f'Failed to block {user.username}\'s account. Current blocked status: {user.blocked}.'
        app.logger.info(info) if success else app.logger.error(error)
        return success

    @staticmethod
    def reset_password(user, new_password):
        hashed_pw = util.hash_data(new_password)
        success = mongo.reset_password(user_id=user.id, hashed_pw=hashed_pw).modified_count
        info = f'{user.username} reset their password.'
        error = f'Failed to reset password for {user.username}.'
        app.logger.info(info) if success else app.logger.error(error)
        return success

    @staticmethod
    def update_username(user, new):
        old = user.username
        success = mongo.update_username(user.id, new).modified_count
        info = f'{old} changed their username to {new}.'
        error = f'Failed to update username {old}. Requested: {new}.'
        app.logger.info(info) if success else app.logger.error(error)
        return success

    @staticmethod
    def get_blacklist():
        return mongo.get_blacklist()

    @staticmethod
    def get_credential_availability(username, ph):
        username_availability = not mongo.get_user_data_by_username(username.upper())
        ph_availability = not mongo.get_user_data_by_phonenumber(ph)
        credential_availability = {
            'Username': username_availability,
            'PhoneNumber': ph_availability
        }
        return credential_availability
