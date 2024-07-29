from SMSAlertService.alert import Alert
from SMSAlertService.dao import DAO
from SMSAlertService.reddit import Reddit
from SMSAlertService.services.alert_service import AlertService


class AlertEngine:

    @staticmethod
    def run():
        posts = Reddit.get_new_posts()
        alerts = AlertEngine.create_alerts_for_many(posts)
        AlertService.send_alerts(alerts)
        return alerts

    @staticmethod
    def create_alerts_for_many(posts):
        alerts = []
        for post in posts:
            subreddit = post.subreddit.display_name
            users = DAO.get_active_users_by_subreddit(subreddit)
            batch = AlertEngine.create_alerts_for_one(post, users)
            alerts.extend(batch)
        return alerts

    @staticmethod
    def create_alerts_for_one(post, users):
        return [
            Alert(
                user=user,
                post=post,
                keywords=keywords
            )
            for user in users
            if (keywords := AlertEngine.find_keywords_in_post(keywords=user.keywords, post=post))
        ]

    @staticmethod
    def find_keywords_in_post(keywords, post):
        return [
            keyword
            for keyword in keywords
            if AlertEngine.keyword_found_in_post(keyword, post)
        ]

    @staticmethod
    def keyword_found_in_post(keyword, post):
        title = post.title.lower()
        body = post.selftext.lower()
        keyword = keyword.lower()
        return (
                keyword in title or
                keyword in body or
                keyword + "s" in title or
                keyword + "s" in body
        )
