import os
import praw
from SMSAlertService import mongo, app


reddit = praw.Reddit(client_id=os.environ['reddit_client_id'],
                     client_secret=os.environ['reddit_client_secret'],
                     user_agent=os.environ['reddit_user_agent'],
                     username=os.environ['reddit_username'],
                     password=os.environ['reddit_password'])

subreddit_name = os.environ['reddit_subreddit']
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
