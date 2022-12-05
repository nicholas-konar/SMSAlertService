import os
import praw
from SMSAlertService import mongo, app

reddit = praw.Reddit(client_id=os.environ.get('REDDIT_CLIENT_ID'),
                     client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
                     user_agent=os.environ.get('REDDIT_USER_AGENT'),
                     username=os.environ.get('REDDIT_USERNAME'),
                     password=os.environ.get('REDDIT_PASSWORD'))

subreddit_name = os.environ.get('REDDIT_SUBREDDIT')
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
