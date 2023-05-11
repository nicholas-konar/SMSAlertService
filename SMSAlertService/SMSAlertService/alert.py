from SMSAlertService import util, app


class Alert:

    def __init__(self, user, post):
        self.owner = user
        self.post = post
        self.destination = user.phonenumber
        self.subreddit = post.subreddit.display_name
        self.url = post.url
        self.keywords = util.format_keywords(user.keyword_hits)
        self.units_left = user.units_left - 1

