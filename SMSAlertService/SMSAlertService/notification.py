from SMSAlertService import app, mongo, reddit, twilio


def distribute():
    messages_sent = 0
    new_post = False
    if reddit.has_new_post():
        new_post = True
        post = reddit.get_latest_post()
        users = mongo.get_users()
        for user in users:
            matching_keywords = []
            for keyword in user['Keywords']:
                if keyword.lower() in str(post.title).lower() or keyword in str(post.selftext).lower():
                    app.logger.debug('keyword match: ' + keyword)
                    matching_keywords.append(keyword + ', ')
            if matching_keywords and not blacklisted(user):
                twilio.send(user['Username'], user['PhoneNumber'], post.url, matching_keywords)
                messages_sent += 1
    response = {
        "NewPost": new_post,
        "MessagesSent": messages_sent
    }
    return response


def blacklisted(user):
    blacklist = mongo.get_blacklist()
    app.logger.info('Checking blacklist for ' + user['PhoneNumber'])
    for number in blacklist:
        if user['PhoneNumber'] == number:
            app.logger.debug('Blacklisted number detected: ' + user['PhoneNumber'])
            return True
    return False
