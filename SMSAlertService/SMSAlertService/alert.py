import os
from SMSAlertService import util


class Alert:
    owner = ''
    destination = ''
    url = ''
    keywords = []
    units_left = ''
    body = ''
    twilio_data = None

    def __init__(self, user, url, keywords, subreddit):
        self.owner = user['Username']
        self.destination = user['PhoneNumber']
        self.url = url
        self.keywords = util.format_keywords(keywords)
        self.units_left = int(user['Units'] - 1)

        if self.units_left == 0:
            self. body = f'You\'re out of alerts! Reload at www.smsalertservice.com/profile' \
                   f'\n\nA post on {subreddit} matched the following keywords: {self.keywords}\n{url}'
        elif self.units_left < 5:
            self. body = f'You only have {self.units_left} alert(s) left! Reload at www.smsalertservice.com/profile\n\n' \
                   f'A post on {subreddit} matched the following keywords: {self.keywords}\n{url}'
        else:
            self. body = f'www.smsalertservice.com\n\nA post on {subreddit} matched the following keywords: {self.keywords}\n{url}'

