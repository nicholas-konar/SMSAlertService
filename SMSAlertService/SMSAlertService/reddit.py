import configparser
import os
import praw
from SMSAlertService import mongo, app

config = configparser.RawConfigParser()
folder = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(folder, 'config.init')
config.read(file)


reddit = praw.Reddit(client_id=config.get('reddit', 'client_id'),
                     client_secret=config.get('reddit', 'client_secret'),
                     user_agent=config.get('reddit', 'user_agent'),
                     username=config.get('reddit', 'username'),
                     password=config.get('reddit', 'password'))

subreddit_name = config.get('reddit', 'subreddit')
subreddit = reddit.subreddit(subreddit_name)


def has_new_post():
    post = get_latest_post()
    last_post_id = mongo.get_last_post_id()
    if post.id != last_post_id:
        set_last_post(post)
        app.logger.info('New PostId: ' + post.id)
        return True
    else:
        app.logger.info('No new posts yet.')
        return False


def get_latest_post():
    for post in subreddit.new(limit=1):
        return post


def set_last_post(post):
    mongo.save_post_data(post)
