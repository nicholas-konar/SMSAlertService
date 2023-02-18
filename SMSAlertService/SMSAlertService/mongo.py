import math
import os
import secrets
import string

import arrow
import bcrypt
import pymongo

from SMSAlertService import app, util

# NO VPN
# In compass, enter regular_url value from below, then select default tls and upload mongodb.pem in the second file upload box (nothing in the first)

# to get the certs to work, in the command line say:
# python3 -m pip install certifi
# export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")


url = os.environ['MONGO_URL_PROD']
client = pymongo.MongoClient(url, tls=True)

db_name = os.environ['MONGO_DB_PROD']
db = client.get_database(db_name)
user_records = db.user_data
app_records = db.app_data
promo_code_records = db.promo_code_data


def create_user(username, password, phonenumber):
    timestamp = arrow.now().format('MM-DD-YYYY HH:mm:ss')
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user_data = {
        'SignUpDate': timestamp,
        'Password': hashed_pw,
        'Username': username,
        'PhoneNumber': phonenumber,
        'Verified': False,
        'OTP': None,
        'TotalRevenue': 0,
        'Units': 10,
        'UnitsSent': 0,
        'UnitsPurchased': 0,
        'TwilioRecords': [],
        'SalesRecords': [],
        'PromoCodeRecords': [],
        'Keywords': []
    }
    user_records.insert_one(user_data)
    app.logger.info(f"Created user {username} in database")


def verify(username):
    if not is_verified(username):
        query = {"Username": username}
        value = {"$set": {"Verified": True}}
        user_records.update_one(query, value)
        app.logger.info(f'User {username}\'s phonenumber has been verified.')


def is_verified(username):
    user = get_user_by_username(username)
    try:
        return user['Verified']
    except KeyError:
        return False


def process_transaction(username, units_purchased, amount):
    timestamp = arrow.now().format("MM-DD-YYYY HH:mm:ss")

    old_unit_count = get_message_count(username)
    updated_unit_count = old_unit_count + int(units_purchased)

    user = get_user_by_username(username)
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

    user_records.update_one(query, new_value)
    app.logger.info(f'Purchase complete')


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
        promo_code_records.insert_one(promo_code_data)
        app.logger.info(f"Created Promo Code '{code}' ({i+1} of {quantity})")


def get_code(promo_code):
    return promo_code_records.find_one({"Code": promo_code})


def get_codes():
    codes = []
    records = promo_code_records.find()
    for code in records:
        codes.append(code)
    return codes


def get_user_by_username(username):
    return user_records.find_one({"Username": username})


def get_user_by_phonenumber(ph):
    return user_records.find_one({"PhoneNumber": ph})


def get_users():
    users = []
    records = user_records.find()
    for user in records:
        users.append(user)
    return users


def get_message_count(username):
    user = get_user_by_username(username)
    return user["Units"]


def update_user_msg_data(username, message):
    timestamp = arrow.now().format("MM-DD-YYYY HH:mm:ss")
    user = get_user_by_username(username)
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
    app.logger.info(f'Unit count reduced by 1 for user {username}')


def reset_password(username, pw):
    hashed_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
    query = {"Username": username}
    value = {"$set": {"Password": hashed_pw}}
    user_records.update_one(query, value)
    app.logger.info(f'New password saved for user {username}')


def save_otp(ph, otp):
    query = {"PhoneNumber": ph}
    value = {"$set": {"OTP": otp}}
    user_records.update_one(query, value)
    app.logger.info(f'OTP {otp} saved successfully')


def add_to_blacklist(phonenumber):
    query = {"Document": "BLACKLIST"}
    new_value = {"$push": {"Keywords": phonenumber}}
    app_records.update_one(query, new_value)
    app.logger.info('Added ' + phonenumber + 'to blacklist')


def get_blacklist():
    document = app_records.find_one({"Document": "BLACKLIST"})
    return document['Blacklist']


def blacklisted(user):
    blacklist = get_blacklist()
    app.logger.info('Checking blacklist for ' + user['PhoneNumber'])
    for number in blacklist:
        if user['PhoneNumber'] == number:
            app.logger.info(f'Blacklisted number detected for user {user["Username"]}: {user["PhoneNumber"]}')
            return True
    return False


def get_keywords(username):
    user = user_records.find_one({"Username": username})
    return user['Keywords']


def add_keyword(username, keyword):
    keywords = get_keywords(username)
    if keyword not in keywords:
        query = {"Username": username}
        value = {"$push": {"Keywords": keyword}}
        user_records.update_one(query, value)
        app.logger.info(f'User {username} added keyword {keyword}')


def delete_keyword(username, keyword):
    query = {"Username": username}
    value = {"$pull": {"Keywords": keyword}}
    user_records.update_one(query, value)
    app.logger.info(f'User {username} deleted keyword {keyword}')


def delete_all_keywords(username):
    query = {"Username": username}
    new_value = {"$set": {"Keywords": []}}
    user_records.update_one(query, new_value)
    app.logger.info(f'User {username} deleted all keywords')


def get_phonenumber(username):
    user = get_user_by_username(username)
    return user['PhoneNumber']


def update_phonenumber(username, phonenumber):
    query = {"Username": username}
    new_value = {"$set": {"PhoneNumber": phonenumber}}
    user_records.update_one(query, new_value)
    app.logger.info('User ' + username + ' updated PhoneNumber to ' + phonenumber)


def update_username(old_username, new_username):
    query = {"Username": old_username}
    new_value = {"$set": {"Username": new_username}}
    user_records.update_one(query, new_value)
    app.logger.info('User ' + old_username + ' changed username to ' + new_username)


def phonenumber_taken(phonenumber):
    return user_records.find_one({"PhoneNumber": phonenumber})


def username_taken(username):
    return user_records.find_one({"Username": username})


# -------------------------------- REDDIT POST MANAGEMENT --------------------------------
def get_last_post_id():
    document = app_records.find_one({"Document": "POST_INFO"})
    last_post_id = document["LastPostId"]
    app.logger.info('LastPostId: ' + last_post_id)
    return last_post_id


def save_post_id(post):
    query = {"Document": "POST_INFO"}
    last_post_id = {"$set": {
        "LastPostId": post.id
    }}
    app_records.update_one(query, last_post_id)
    app.logger.info('LastPostId is now ' + post.id)
