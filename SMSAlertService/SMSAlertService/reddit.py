import os
import praw
from SMSAlertService import mongo, app

reddit = praw.Reddit(client_id=os.environ['REDDIT_CLIENT_ID'],
                     client_secret=os.environ['REDDIT_CLIENT_SECRET'],
                     user_agent=os.environ['REDDIT_USER_AGENT'],
                     username=os.environ['REDDIT_USERNAME'],
                     password=os.environ['REDDIT_PASSWORD'])

subreddit_name = os.environ['REDDIT_SUBREDDIT']
subreddit = reddit.subreddit(subreddit_name)


def new_post():
    post = get_latest_post()
    last_post_id = mongo.get_last_post_id()
    if post.id != last_post_id:
        app.logger.info('New PostId: ' + post.id)
        mongo.save_post_id(post)
        return post
    else:
        app.logger.info('No new posts yet.')
        return False


def get_latest_post():
    for post in subreddit.new(limit=1):
        return post

