from SMSAlertService import app, mongo, reddit, twilio, util


def run():
    messages_sent = 0
    post = reddit.new_post()
    if post:
        if '[wts]' in post.title.lower():
            users = mongo.get_users()
            for user in users:
                matching_keywords = []
                for keyword in user['Keywords']:
                    if util.keyword_match(user, keyword, post):
                        matching_keywords.append(keyword + ', ')
                if matching_keywords and int(user['Units']) > 0 and not mongo.blacklisted(user):
                    message = twilio.send_alert(user['Username'], user['PhoneNumber'], post.url,
                                                matching_keywords, int(user['Units'] - 1))
                    mongo.update_user_msg_data(user['Username'], message)
                    messages_sent += 1
    response = {
        "NewPost": str(post),
        "MessagesSent": messages_sent
    }
    return response


def send_otp(ph):
    otp = util.generate_otp()
    mongo.save_otp(ph, otp)
    twilio.send_otp(ph, otp)
