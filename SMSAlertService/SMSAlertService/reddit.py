import os
import praw
from SMSAlertService import mongo, app, config

GUNACCESSORIESFORSALE = 'GunAccessoriesForSale'
GEARTRADE = 'GearTrade'
GUNDEALS = 'gundeals'

SUBREDDITS = [GUNACCESSORIESFORSALE, GEARTRADE, GUNDEALS]

reddit = praw.Reddit(client_id=os.environ['REDDIT_CLIENT_ID'],
                     client_secret=os.environ['REDDIT_CLIENT_SECRET'],
                     user_agent=os.environ['REDDIT_USER_AGENT'],
                     username=os.environ['REDDIT_USERNAME'],
                     password=os.environ['REDDIT_PASSWORD'])


def get_new_posts():
    post_data = mongo.get_post_data()
    posts = []
    for subreddit in SUBREDDITS:
        post = get_latest_post(subreddit)
        last_known_post_id = post_data[f'${subreddit}']['LastPostId']
        app.logger.debug(f'Last known {subreddit} post id: {last_known_post_id}')
        app.logger.debug(f'Current {subreddit} post id: {post.id}')
        if post.id != last_known_post_id and '[WTS]' in post.title.upper(): # todo: relocate WTS filter or make filter class
            mongo.save_post_id(post)
            posts.append(post)
            app.logger.info(f'New post in r/{subreddit}: {post.id}')
    return posts


def get_latest_post(subreddit):
    for post in reddit.subreddit(subreddit).new(limit=1):
        return post

