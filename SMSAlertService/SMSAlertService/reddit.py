import json
import os
import praw
from SMSAlertService import app
from SMSAlertService.dao import DAO

reddit = praw.Reddit(
    client_id=os.environ['REDDIT_CLIENT_ID'],
    client_secret=os.environ['REDDIT_CLIENT_SECRET'],
    user_agent=os.environ['REDDIT_USER_AGENT'],
    username=os.environ['REDDIT_USERNAME'],
    password=os.environ['REDDIT_PASSWORD']
)


class Reddit:

    @staticmethod
    def get_new_posts():
        subreddits = DAO.get_reddit_data()
        posts = []
        for subreddit in subreddits:
            post = Reddit.get_current_post(subreddit['Subreddit'])
            previous_post_id = subreddit['LastPostId']

            if post.id != previous_post_id and 'WTB' not in post.title.upper():  # todo: relocate WTS filter or make filter class
                DAO.update_post_id(post)
                posts.append(post)
                app.logger.info(f'New post in r/{subreddit["Subreddit"]}: {post.id}')

        return posts

    @staticmethod
    def get_current_post(subreddit):
        return [post for post in reddit.subreddit(subreddit).new(limit=1)][0]
