from SMSAlertService import app, mongo, reddit, message


def send():
    matching_keywords = []
    messages_sent = 0
    new_post = False
    if reddit.has_new_post():
        new_post = True
        post = reddit.get_latest_post()
        users = mongo.get_users()
        for user in users:
            try:
                if user['Messages'] > 0:
                    for keyword in user['Keywords']:
                        if keyword.lower() in str(post.title).lower() or keyword in str(post.selftext).lower():
                            matching_keywords.append(keyword + ', ')
                    if matching_keywords:
                        app.logger.debug('Keyword match detected: ' + str(matching_keywords))
                        app.logger.debug('Sending SMS to ' + user['Username'] + ' at ' + user[
                            'PhoneNumber'])
                        message.send(user['PhoneNumber'], post.url, matching_keywords)
                        messages_sent += 1
            except KeyError as key:
                app.logger.error(
                    'Error parsing the following key in database: ' + str(key) + " for User " + str(user['Username']))
                continue
    response = {
        "NewPost": new_post,
        "KeywordsMatched": len(matching_keywords),
        "MessagesSent": messages_sent
    }
    return response
