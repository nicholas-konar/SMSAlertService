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
                    app.logger.debug(f'Keyword match detected for user {user["Username"]}: "{keyword}"')
                    matching_keywords.append(keyword + ', ')
            if matching_keywords and not mongo.blacklisted(user):
                message = twilio.send(user['Username'], user['PhoneNumber'], post.url, matching_keywords)
                mongo.update_user_msg_data(user['Username'], message)
                messages_sent += 1
    response = {
        "NewPost": new_post,
        "MessagesSent": messages_sent
    }
    return response


