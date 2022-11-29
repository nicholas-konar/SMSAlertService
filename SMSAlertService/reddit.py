import praw

from SMSAlertService import mongo, app

reddit = praw.Reddit(client_id='lOIWSUwdm3Ld2llq-XDEZA',
                     client_secret='1nG-J-vaasQMavUhfB_mmnonlBAnoQ',
                     user_agent='GAFSAlertService',
                     username='GAFSAlertService',
                     password='qaXwuw-7bubsu-caqtec')

subreddit = reddit.subreddit('GunAccessoriesForSale')


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

