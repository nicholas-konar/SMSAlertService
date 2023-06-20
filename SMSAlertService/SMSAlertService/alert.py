from SMSAlertService import util


class Alert:

    def __init__(self, user, post, keywords):
        self.owner = user
        self.post = post
        self.subreddit = post.subreddit.display_name
        self.url = f'redd.it/{post.id}'
        self.keywords = util.format_keywords(keywords)

