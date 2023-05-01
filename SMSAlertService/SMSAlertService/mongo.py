import math
import os
import secrets
import string

import arrow
import bcrypt
import pymongo
from bson.objectid import ObjectId

from SMSAlertService import app, util

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
        'OTP': None,
        'OTPsSent': 0,
        'Verified': verified,
        'Blocked': False,
        'TwilioRecords': [],
        'SalesRecords': [],
        'PromoCodeRecords': [],
    }
    return user_records.insert_one(user_data)


def set_cookie(user_id, cookie):
    query = {"_id": ObjectId(user_id)}
    new_value = {"$set": {"Cookie": cookie}}
    return user_records.update_one(query, new_value)


def verify(username):
    query = {"Username": username}
    value = {"$set": {"Verified": True}}
    return user_records.update_one(query, value)


def process_transaction(username, units_purchased, amount):
    timestamp = arrow.now().format("MM-DD-YYYY HH:mm:ss")

    old_unit_count = get_message_count(username)
    updated_unit_count = old_unit_count + int(units_purchased)

    user = get_user_data_by_username(username)
    updated_units_purchased = user['UnitsPurchased'] + int(units_purchased)
    updated_total_revenue = user["TotalRevenue"] + math.floor(float(amount))

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

    return user_records.update_one(query, new_value)


def redeem(username, code):
    timestamp = arrow.now().format("MM-DD-YYYY HH:mm:ss")
    promo_code = code['Code']
    reward = code['Reward']
    old_unit_count = get_message_count(username)
    updated_unit_count = old_unit_count + int(reward)

    query = {"Username": username}
    new_value = {
        "$set": {
            "Units": updated_unit_count,
        },
        "$push": {
            "PromoCodeRecords": {
                "Date": timestamp,
                "Code": promo_code,
                "Reward": reward
            }
        }
    }

    user_records.update_one(query, new_value)
    app.logger.info(f'{username} redeemed code {code} for {reward} units')


def process_promo_code(username, promo_code):
    try:
        code = get_code(promo_code)
        if code['Active']:
            redeem(username, code)
            deactivate_code(code, username)
            app.logger.info(f'Processing complete for promo code {promo_code}')
            return code
        else:
            app.logger.info(
                f'Failure to process promo code {promo_code} for user {username}: Code not active')
            return False
    except TypeError as e:
        app.logger.info(f'Failure to process promo code {promo_code} for user {username}: Invalid code \n{e}')
        return False


def deactivate_code(code, username):
    timestamp = arrow.now().format('MM-DD-YYYY HH:mm:ss')
    value = code['Code']
    query = {'Code': value}
    promo_code_data = {
        '$set': {
            'Active': False,
            'RedeemedBy': username,
            'DeactivationDate': timestamp, }
    }
    promo_code_records.update_one(query, promo_code_data)
    app.logger.info(f"Deactivated code {code['Code']}")


def create_promo_codes(reward, quantity, distributor, prefix):
    timestamp = arrow.now().format('MM-DD-YYYY HH:mm:ss')
    distributor = distributor.upper()
    batch = int(quantity)
    for i in range(batch):
        code = util.generate_code(prefix)
        promo_code_data = {
            'Code': code,
            'Reward': reward,
            'Active': True,
            'RedeemedBy': "",
            'Distributor': distributor,
            'ActivationDate': timestamp,
            'DeactivationDate': ""
        }
        return promo_code_records.insert_one(promo_code_data)


def get_code(promo_code):
    return promo_code_records.find_one({"Code": promo_code})


def get_codes():
    codes = []
    records = promo_code_records.find()
    for code in records:
        codes.append(code)
    return codes


# todo: need get all users query

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
    new_value = {
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

    return user_records.update_one(query, new_value)


def reset_password(username, pw):
    hashed_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
    query = {"Username": username}
    value = {"$set": {"Password": hashed_pw}}
    return user_records.update_one(query, value)


def save_otp_data(user, otp):
    timestamp = arrow.now().format("MM-DD-YYYY HH:mm:ss")
    query = {"Username": user.username}
    value = {
        "$set": {
            "OTP": otp.value,
            "OTPsSent": user.otps_sent
        },
        "$push": {
            "TwilioRecords": {
                "Date": timestamp,
                "Type": "OTP",
                "Body": otp.twilio.body,
                "Status": otp.twilio.status,
                "ErrorMessage": otp.twilio.error_message,
                "SID": otp.twilio.sid
            }
        }
    }
    return user_records.update_one(query, value)


def add_to_blacklist(phonenumber):
    query = {"Document": "BLACKLIST"}
    new_value = {"$push": {"Blacklist": phonenumber}}
    return app_records.update_one(query, new_value)


def get_blacklist():
    document = app_records.find_one({"Document": "BLACKLIST"})
    return document['Blacklist']


def block(username):
    query = {"Username": username}
    value = {"$set": {"Blocked": True}}
    return user_records.update_one(query, value)


def add_keyword(username, keyword):
    query = {"Username": username}
    value = {"$push": {"Keywords": keyword}}
    return user_records.update_one(query, value)


def delete_keyword(username, keyword):
    query = {"Username": username}
    value = {"$pull": {"Keywords": keyword}}
    return user_records.update_one(query, value)


def delete_all_keywords(username):
    query = {"Username": username}
    new_value = {"$set": {"Keywords": []}}
    return user_records.update_one(query, new_value)


def update_phonenumber(username, phonenumber):
    query = {"Username": username}
    new_value = {"$set": {"PhoneNumber": phonenumber}}
    user_records.update_one(query, new_value)
    app.logger.info('User ' + username + ' updated PhoneNumber to ' + phonenumber)


def update_username(old_username, new_username):
    query = {"Username": old_username}
    new_value = {"$set": {"Username": new_username}}
    return user_records.update_one(query, new_value)


def get_post_data():
    document = app_records.find_one({"Document": "REDDIT"})
    app.logger.debug(f'POST DATA: {document}')
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
