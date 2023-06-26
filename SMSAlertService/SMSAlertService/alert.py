from SMSAlertService import util, app


class Alert:

    def __init__(self, user, post, keywords):
        self.owner = user
        self.post = post
        self.subreddit = post.subreddit.display_name.replace('Gun', '***')
        self.url = f'redd.it/{post.id}'
        self.keywords = util.format_keywords(keywords)
        app.logger.info(f'Preparing alert for {user.username}: r/{self.subreddit} - {self.keywords}')

