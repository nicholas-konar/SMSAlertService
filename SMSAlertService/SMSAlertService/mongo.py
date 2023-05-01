import math
import os
import arrow
import pymongo

from bson.objectid import ObjectId

# NO VPN
# In compass, enter regular_url value from below, then select default tls and upload mongodb.pem in the second file upload box (nothing in the first)

# to get the certs to work, in the command line say:
# python3 -m pip install certifi
# export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")


url = os.environ['MONGO_URL']
client = pymongo.MongoClient(url, tls=True)

db_name = os.environ['MONGO_DB_NAME']
db = client.get_database(db_name)
user_records = db.user_data
app_records = db.app_data
promo_code_records = db.promo_code_data


def create_user(username, pw_hash, phonenumber, verified, timestamp, cookie):
    user_data = {
        'Cookie': cookie,
        'SignUpDate': timestamp,
        'Password': pw_hash,
        'Username': username,
        'PhoneNumber': phonenumber,
        'Subreddits': [],
        'Keywords': [],
        'TotalRevenue': 0,
        'Units': 0,
        'UnitsSent': 0,
        'UnitsPurchased': 0,
        'Verified': verified,
        'Blocked': False,
        'TwilioRecords': [],
        'SalesRecords': []
    }
    return user_records.insert_one(user_data)


def set_cookie(user_id, cookie):
    query = {"_id": ObjectId(user_id)}
    value = {"$set": {"Cookie": cookie}}
    return user_records.update_one(query, value)


# todo: this needs help
def process_transaction(username, units_purchased, amount):
    timestamp = arrow.now().format("MM-DD-YYYY HH:mm:ss")

    old_unit_count = get_message_count(username)
    updated_unit_count = old_unit_count + int(units_purchased)

    user = get_user_data_by_username(username)
    updated_units_purchased = user['UnitsPurchased'] + int(units_purchased)
    updated_total_revenue = user["TotalRevenue"] + math.floor(float(amount))

    query = {"Username": username}
    value = {
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

    return user_records.update_one(query, value)


def get_all_user_data():
    return user_records.find()


def get_all_active_user_data():
    return user_records.find({"Units": {"$gt": 0}})


def get_user_data_by_id(user_id):
    return user_records.find_one({"_id": ObjectId(user_id)})


def get_user_data_by_username(username):
    return user_records.find_one({"Username": username})


def get_user_data_by_phonenumber(ph):
    return user_records.find_one({"PhoneNumber": ph})


def save_alert_data(alert):
    timestamp = arrow.now().format("MM-DD-YYYY HH:mm:ss")
    user = get_user_data_by_username(alert.owner.username)
    updated_msg_count = user["Units"] - 1
    updated_sent_count = user["UnitsSent"] + 1

    query = {"Username": alert.owner.username}
    value = {
        "$set": {
            "Units": updated_msg_count,
            "UnitsSent": updated_sent_count
        },
        "$push": {
            "TwilioRecords": {
                "Date": timestamp,
                "Type": "Alert",
                "Body": alert.twilio.body,
                "Status": alert.twilio.status,
                "ErrorMessage": alert.twilio.error_message,
                "SID": alert.twilio.sid
            }
        }
    }
    return user_records.update_one(query, value)


def reset_password(user_id, hashed_pw):
    query = {"_id": ObjectId(user_id)}
    value = {"$set": {"Password": hashed_pw}}
    return user_records.update_one(query, value)


def add_to_blacklist(phonenumber):
    query = {"Document": "BLACKLIST"}
    new_value = {"$push": {"Blacklist": phonenumber}}
    return app_records.update_one(query, new_value)


def get_blacklist():
    document = app_records.find_one({"Document": "BLACKLIST"})
    return document['Blacklist']


def block(user_id):
    query = {"_id": ObjectId(user_id)}
    value = {"$set": {"Blocked": True}}
    return user_records.update_one(query, value)


def add_keyword(user_id, keyword):
    query = {"_id": ObjectId(user_id)}
    value = {"$push": {"Keywords": keyword}}
    return user_records.update_one(query, value)


def delete_keyword(user_id, keyword):
    query = {"_id": ObjectId(user_id)}
    value = {"$pull": {"Keywords": keyword}}
    return user_records.update_one(query, value)


def delete_all_keywords(user_id):
    query = {"_id": ObjectId(user_id)}
    value = {"$set": {"Keywords": []}}
    return user_records.update_one(query, value)


def update_phonenumber(user_id, phonenumber):
    query = {"_id": ObjectId(user_id)}
    value = {"$set": {"PhoneNumber": phonenumber}}
    return user_records.update_one(query, value)


def update_username(user_id, new_username):
    query = {"_id": ObjectId(user_id)}
    value = {"$set": {"Username": new_username}}
    return user_records.update_one(query, value)


def get_reddit_data():
    document = app_records.find_one({"Document": "REDDIT"})
    return document["SubReddits"]


def save_post_id(post):
    query = {"Document": "REDDIT"}
    value = {"$set": {
        f"SubReddits.${post.subreddit.display_name}": {
            "LastPostId": post.id
        }}}
    return app_records.update_one(query, value, upsert=True)

# def add_field_to_all_users():
#     app.logger.info(f'adding field to all users')
#     users = get_user_data()
#     for user in users:
#         query = {"Username": user["Username"]}
#         value = {"$set": {"Blocked": False}}
#         user_records.update_one(query, value)
