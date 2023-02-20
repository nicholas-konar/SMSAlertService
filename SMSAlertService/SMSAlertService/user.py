from SMSAlertService import util, app


class User:
    username = ''
    phonenumber = ''
    keywords = []
    matching_keywords = []
    units_left = 0
    otps_sent = 0
    blocked = False

    def __init__(self, user_data):
        self.username = user_data['Username']
        self.phonenumber = user_data['PhoneNumber']
        self.keywords = user_data['Keywords']
        self.units_left = int(user_data['Units'])
        self.otps_sent = int(user_data['OTPsSent'])
        self.blocked = user_data['Blocked']

    def requires_alert_for(self, post):
        if self.units_left <= 0:
            return False
        else:
            for keyword in self.keywords:
                if util.detect_keyword(keyword, post):
                    self.matching_keywords.append(keyword)
                    app.logger.info(f'Keyword detected in post for user {self.username}: "{keyword}"')
                    return True
                else:
                    return False
