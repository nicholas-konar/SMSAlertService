import json


class User:
    def __init__(self, user_data):
        self.username = user_data['Username']
        self.password = user_data['Password']
        self.phonenumber = user_data['PhoneNumber']
        self.keywords = user_data['Keywords']
        self.units_left = int(user_data['Units'])
        self.otps_sent = int(user_data['OTPsSent'])
        self.verified = user_data['Verified']
        self.blocked = user_data['Blocked']
        self.keyword_hits = []

    def requires_alert_for_post(self, post):
        if self.eligible():
            self.set_keyword_hits_from_post(post)
            return bool(self.keyword_hits)
        else:
            return False

    def eligible(self):
        return self.units_left > 0 and self.verified

    def set_keyword_hits_from_post(self, post):
        for keyword in self.keywords:
            if (post.subreddit.display_name in keyword['Subreddits'] and
                    self.keyword_found_in_post(keyword['Keyword'], post)):
                self.keyword_hits.append(keyword)

    def keyword_found_in_post(self, keyword, post):
        lower_title = str(post.title).lower()
        lower_selftext = str(post.selftext).lower()
        return (f" {keyword.lower()} " in f" {lower_title} " or
                f" {keyword.lower()} " in f" {lower_selftext} " or
                f" {keyword.lower()}s " in f" {lower_title} " or
                f" {keyword.lower()}s " in f" {lower_selftext} ")

    def get_keywords_json(self):
        keywords = [keyword['Keyword'] for keyword in self.keywords]
        return json.dumps(keywords)
