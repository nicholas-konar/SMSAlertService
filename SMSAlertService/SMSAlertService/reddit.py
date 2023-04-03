import os
import praw
from SMSAlertService import mongo, app

reddit = praw.Reddit(client_id=os.environ['REDDIT_CLIENT_ID'],
                     client_secret=os.environ['REDDIT_CLIENT_SECRET'],
                     user_agent=os.environ['REDDIT_USER_AGENT'],
                     username=os.environ['REDDIT_USERNAME'],
                     password=os.environ['REDDIT_PASSWORD'])
subreddits = ['GunAccessoriesForSale']
# subreddit_name = os.environ['REDDIT_SUBREDDIT']
# subreddit = reddit.subreddit(subreddit_name)


def get_latest_posts():
    post_data = mongo.get_post_data()
    posts = []
    for subreddit_name in subreddits:
        post = get_latest_post(subreddit_name)
        last_known_post_id = post_data[f'{subreddit_name}']['LastPostId']
        if post.id != last_known_post_id: # todo: relocate WTS filter or make filter class
            mongo.save_post_id(post)
            posts.append(post)
            app.logger.info(f'New post in r/{subreddit_name}: {post.id}')
    return posts


def get_latest_post(subreddit_name):
    for post in reddit.subreddit(subreddit_name).new(limit=1):
        return post

