import os
import arrow
import bcrypt
import pymongo

from SMSAlertService import app

# NO VPN
# In compass, enter regular_url value from below, then select default tls and upload mongodb.pem in the second file upload box (nothing in the first)

# to get the certs to work, in the command line say:
# python3 -m pip install certifi
# export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")
# and use pymongo.MongoClient(regular_url, tls=True) in the code


app.secret_key = os.environ.get('MONGO_SECRET_KEY')
url = os.environ.get('MONGO_URL')
client_DEV = pymongo.MongoClient(url, tls=True)

db_dev_name = os.environ.get('MONGO_DB_DEV')
db_DEV = client_DEV.get_database(db_dev_name)
user_records = db_DEV.user_data
app_records = db_DEV.app_data


def create_user(username, password, phonenumber):
    timestamp = arrow.now().format('MM-DD-YYYY HH:mm:ss')
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user_data = {
        'SignUpDate': timestamp,
        'Password': hashed_pw,
        'Username': username,
        'PhoneNumber': phonenumber,
        'TotalRevenue': 0,
        'Units': 0,
        'UnitsSent': 0,
        'UnitsPurchased': 0,
        'TwilioRecords': [],
        'SalesRecords': [],
        'Keywords': []
    }
    user_records.insert_one(user_data)
    app.logger.info(f"Created new user '{username}'")


def process_transaction(username, units_purchased, amount):
    timestamp = arrow.now().format("MM-DD-YYYY HH:mm:ss")

    old_unit_count = get_message_count(username)
    updated_unit_count = old_unit_count + int(units_purchased)

    user = get_user(username)
    updated_units_purchased = user['UnitsPurchased'] + int(units_purchased)
    updated_total_revenue = user["TotalRevenue"] + float(amount)

    query = {"Username": username}
    new_value = {
        "$set": {
                "Units": updated_unit_count,
                "UnitsPurchased": updated_units_purchased,
                "TotalRevenue": updated_total_revenue
            },
        "$push": {
                "SalesRecords": {
                    "Date": timestamp,
                    "Units": units_purchased,
                    "Revenue": amount
                }
            }
        }

    user_records.update_one(query, new_value)
    app.logger.debug(f'{username} just purchased {units_purchased} units')


def get_user(username):
    return user_records.find_one({"Username": username})


def get_message_count(username):
    user = get_user(username)
    return user["Units"]


def update_user_msg_data(username, message):
    timestamp = arrow.now().format("MM-DD-YYYY HH:mm:ss")
    user = get_user(username)
    updated_msg_count = user["Units"] - 1
    updated_sent_count = user["UnitsSent"] + 1

    query = {"Username": username}
    new_value = {
        "$set": {
                "Units": updated_msg_count,
                "UnitsSent": updated_sent_count
            },
        "$push": {
                "TwilioRecords": {
                    "Date": timestamp,
                    "Status": message.status,
                    "MessageSID": message.sid,
                    "Body": message.body,
                    "ErrorMessage": message.error_message
                }
            }
        }

    user_records.update_one(query, new_value)
    app.logger.debug(f'Unit count reduced by 1 for user {username}')


def get_users():
    return user_records.find()


def get_subscription_status(username):
    user = user_records.find_one({"Username": username})
    return user['Subscription']['Active']


def reset_password(phonenumber, password):
    phonenumber = phonenumber[2:]  # trims the +1 off the ph. number
    app.logger.debug('full phone = ' + phonenumber)
    query = {"PhoneNumber": phonenumber}
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    app.logger.debug('pw hash = ' + str(hashed_pw))
    new_value = {"$set": {"Password": hashed_pw}}
    user_records.update_one(query, new_value)


def activate_subscription(username, subscription_id):
    timestamp = arrow.now().format('MM-DD-YYYY HH:mm:ss')
    query = {"Username": username}
    value = {
        "$set": {
            "Subscription": {
                "Active": True,
                "ID": subscription_id
            }
        }}
    user_records.update_one(query, value)
    value = {
        "$push": {
            "SubscriptionHistory": {
                "ID": subscription_id,
                "Action": "SUBSCRIBE",
                "Timestamp": timestamp
            }
        }}
    user_records.update_one(query, value)
    app.logger.info('SubscriptionId ' + subscription_id + ' now linked to User ' + username)


def suspend(subscription_id):
    timestamp = arrow.now().format('MM-DD-YYYY HH:mm:ss')
    users = get_users()
    for user in users:
        if user['Subscription']['ID'] == subscription_id:
            username = user['Username']
            query = {"Username": username}
            value = {
                "$set": {
                    "Subscription": {
                        "ID": subscription_id,
                        "Active": False,
                    }
                }}
            user_records.update_one(query, value)
            value = {
                "$push": {
                    "SubscriptionHistory": {
                        "ID": subscription_id,
                        "Action": "SUSPEND",
                        "Timestamp": timestamp
                    }
                }}
            user_records.update_one(query, value)
            app.logger.info(
                'Deactivated User ' + username + 'because Subscription ' + subscription_id + ' was suspended.')


def deactivate(subscription_id):
    timestamp = arrow.now().format('MM-DD-YYYY HH:mm:ss')
    users = get_users()
    for user in users:
        if user['Subscription']['ID'] == subscription_id:
            username = user['Username']
            query = {"Username": username}
            value = {
                "$set": {
                    "Subscription": {
                        "ID": subscription_id,
                        "Active": False,
                    }
                }}
            user_records.update_one(query, value)
            value = {
                "$push": {
                    "SubscriptionHistory": {
                        "ID": subscription_id,
                        "Action": "CANCEL",
                        "Timestamp": timestamp
                    }
                }}
            user_records.update_one(query, value)
            app.logger.info(
                'Deactivated User ' + username + 'because Subscription ' + subscription_id + ' was canceled.')


def add_to_blacklist(phonenumber):
    query = {"Document": "Blacklist"}
    new_value = {"$push": {"Keywords": phonenumber}}
    app_records.update_one(query, new_value)
    app.logger.debug('Added ' + phonenumber + 'to blacklist')


def get_blacklist():
    blacklist = app_records.find_one({"Document": "Blacklist"})
    return blacklist['Blacklist']


def blacklisted(user):
    blacklist = get_blacklist()
    app.logger.info('Checking blacklist for ' + user['PhoneNumber'])
    for number in blacklist:
        if user['PhoneNumber'] == number:
            app.logger.debug(f'Blacklisted number detected for user {user["Username"]}: {user["PhoneNumber"]}')
            return True
    return False


def get_keywords(username):
    user = user_records.find_one({"Username": username})
    return user['Keywords']


def add_keyword(username, keyword):
    query = {"Username": username}
    new_value = {"$push": {"Keywords": keyword}}
    user_records.update_one(query, new_value)
    app.logger.debug('Added new keyword "' + keyword + '"to User "' + username + '"')


def delete_all_keywords(username):
    query = {"Username": username}
    new_value = {"$set": {"Keywords": []}}
    user_records.update_one(query, new_value)
    app.logger.debug(f'Deleted all keywords in DB for user {username}')


def get_phonenumber(username):
    user = get_user(username)
    return user['PhoneNumber']


def update_phonenumber(username, phonenumber):
    query = {"Username": username}
    new_value = {"$set": {"PhoneNumber": phonenumber}}
    user_records.update_one(query, new_value)
    app.logger.debug('User ' + username + ' updated PhoneNumber to ' + phonenumber)


def update_username(old_username, new_username):
    query = {"Username": old_username}
    new_value = {"$set": {"Username": new_username}}
    user_records.update_one(query, new_value)
    app.logger.debug('User ' + old_username + ' changed username to ' + new_username)


def phonenumber_taken(phonenumber):
    return user_records.find_one({"PhoneNumber": phonenumber})


def username_taken(username):
    return user_records.find_one({"Username": username})


# -------------------------------- REDDIT POST MANAGEMENT --------------------------------
def get_last_post_id():
    doc = app_records.find_one({"Document": "POST_INFO"})
    last_post_id = doc["LastPostID"]
    app.logger.debug('LastPostID: ' + last_post_id)
    return last_post_id


def save_post_data(post):
    timestamp = arrow.now().format("MM-DD-YYYY HH:mm:ss")
    query = {"Document": "POST_INFO"}
    last_post_id = {"$set": {
        "LastPostID": post.id
    }}
    app_records.update_one(query, last_post_id)
    post_log = {
        "$push": {
            "PostLog": {
                "PostID": post.id,
                "URL": post.url,
                "TimeStamp": timestamp
            }
        }}
    app_records.update_one(query, post_log)
    app.logger.debug('LastPostID is now ' + post.id)
