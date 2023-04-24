from SMSAlertService import util, app


class User:
    username = ''
    password = ''
    phonenumber = ''
    keywords = []
    keyword_hits = []
    units_left = 0
    otps_sent = 0
    verified = False
    blocked = False

    def __init__(self, user_data):
        self.username = user_data['Username']
        self.password = user_data['Password']
        self.phonenumber = user_data['PhoneNumber']
        self.keywords = user_data['Keywords']
        self.units_left = int(user_data['Units'])
        self.otps_sent = int(user_data['OTPsSent'])
        self.verified = user_data['Verified']
        self.blocked = user_data['Blocked']

    def requires_alert_for_post(self, post):
        if self.eligible():
            self.set_keyword_hits_from_post(post)
            if len(self.keyword_hits) > 0:
                return True
            else:
                return False
        else:
            return False

    def eligible(self):
        if self.units_left > 0 and self.verified:
            return True
        else:
            return False

    def set_keyword_hits_from_post(self, post):
        for keyword in self.keywords:  # todo: test this
            if post.subreddit.display_name in keyword['Subreddits'] and self.keyword_found_in_post(keyword['Keyword'], post):
                self.keyword_hits.append(keyword)

    def keyword_found_in_post(self, keyword, post):
        if keyword.lower() in str(post.title).lower() \
                or keyword.lower() in str(post.selftext).lower() \
                or keyword.lower() + 's' in str(post.title).lower() \
                or keyword.lower() + 's' in str(post.selftext).lower():
            app.logger.info(f'Keyword detected in post {post.id} for user {self.username}: "{keyword}"')
            return True
        else:
            return False

    def get_keywords_only(self):
        keywords_only = []
        for keyword in self.keywords:
            keywords_only.append(keyword['Keyword'])
        return keywords_only
