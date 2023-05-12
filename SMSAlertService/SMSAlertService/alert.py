from SMSAlertService import util, app


class Alert:

    def __init__(self, user, post):
        self.owner = user
        self.post = post
        self.subreddit = post.subreddit.display_name
        self.url = post.url
        self.keywords_found = util.format_keywords(user.keyword_hits)

