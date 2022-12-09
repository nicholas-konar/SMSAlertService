import os
import praw
from SMSAlertService import mongo, application
from envs import env

reddit = praw.Reddit(client_id=env('REDDIT_CLIENT_ID'),
                     client_secret=env('REDDIT_CLIENT_SECRET'),
                     user_agent=env('REDDIT_USER_AGENT'),
                     username=env('REDDIT_USERNAME'),
                     password=env('REDDIT_PASSWORD'))

subreddit_name = env('REDDIT_SUBREDDIT')
subreddit = reddit.subreddit(subreddit_name)


def has_new_post():
    post = get_latest_post()
    last_post_id = mongo.get_last_post_id()
    if post.id != last_post_id:
        set_last_post(post)
        application.logger.info('New PostId: ' + post.id)
        return True
    else:
        application.logger.info('No new posts yet.')
        return False


def get_latest_post():
    for post in subreddit.new(limit=1):
        return post


def set_last_post(post):
    mongo.save_post_data(post)
