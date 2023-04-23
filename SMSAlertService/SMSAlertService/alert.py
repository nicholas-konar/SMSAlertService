from SMSAlertService import util, app


class Alert:
    owner = {}
    post = {}
    subreddit = ''
    url = ''
    keywords = []
    units_left = 0
    body = ''

    out_of_alerts_message = f'You\'re out of alerts! Reload at www.smsalertservice.com/profile' \
                            f'\n\nA post on {subreddit} matched the following keywords: {keywords}\n{url}'
    low_on_alerts_message = f'You only have {units_left} alert(s) left! Reload at www.smsalertservice.com/profile\n\n' \
                            f'A post on {subreddit} matched the following keywords: {keywords}\n{url}'
    standard_alert_message = f'www.smsalertservice.com\n\nA post on {subreddit} matched the following keywords: {keywords}\n{url}'

    def __init__(self, user, post):
        self.owner = user
        self.post = post
        self.destination = user.phonenumber
        self.subreddit = post.subreddit.display_name
        self.url = post.url
        self.keywords = util.format_keywords(user.keyword_hits)
        self.units_left = user.units_left - 1

    def get_body(self):
        if self.units_left == 0:
            message = f'You\'re out of alerts! Reload at www.smsalertservice.com/profile' \
                            f'\n\nA post on {self.subreddit} matched the following keywords: {self.keywords}\n{self.url}'
            return message
        elif self.units_left <= 5:
            message = f'You only have {self.units_left} alert(s) left! Reload at www.smsalertservice.com/profile\n\n' \
                      f'A post on {self.subreddit} matched the following keywords: {self.keywords}\n{self.url}'
            return message
        else:
            message = f'www.smsalertservice.com\n\nA post on {self.subreddit} matched the following keywords: {self.keywords}\n{self.url}'
            return message
