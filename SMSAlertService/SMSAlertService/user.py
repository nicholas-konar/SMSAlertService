from SMSAlertService import util, app


class User:
    username = ''
    password = ''
    phonenumber = ''
    keywords = []
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

    def eligible(self):
        if self.units_left > 0 and self.verified:
            return True
        else:
            return False

    def get_keyword_hits(self, post):
        keyword_hits = []
        for keyword in self.keywords:  # todo: test this
            if post.subreddit.display_name in keyword['Subreddits'] and self.keyword_found_in_post(keyword, post):
                keyword_hits.append(keyword)
        return keyword_hits

    def keyword_found_in_post(self, keyword, post):
        if keyword.lower() in str(post.title).lower() \
                or keyword.lower() in str(post.selftext).lower() \
                or keyword.lower() + 's' in str(post.title).lower() \
                or keyword.lower() + 's' in str(post.selftext).lower():
            app.logger.info(f'Keyword detected in post {post.id} for user {self.username}: "{keyword}"')
            return True
        else:
            return False
