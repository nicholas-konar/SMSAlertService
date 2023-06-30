import os
import pymongo
from bson import ObjectId, Decimal128

url = os.environ['MONGO_URL']
client = pymongo.MongoClient(url, tls=True, waitQueueTimeoutMS=1000)

db_name = os.environ['MONGO_DB_NAME']
db = client.get_database(db_name)
user_records = db.user_data
app_records = db.app_data
promo_code_records = db.promo_code_data


def create_user(username, pw_hash, phonenumber, verified, timestamp, cookie):
    user_data = {
        'Cookie': cookie,
        'SignUpDate': timestamp,
        'Username': username,
        'Password': pw_hash,
        'PhoneNumber': phonenumber,
        'Verified': verified,
        'Blocked': False,
        'Subreddits': [],
        'Keywords': [],
        'TotalRevenue': 0,
        'Units': 0,
        'UnitsSent': 0,
        'UnitsPurchased': 0,
        'SalesRecords': [],
        'TwilioRecords': []
    }
    return user_records.insert_one(user_data)


def set_cookie(user_id, cookie):
    query = {"_id": ObjectId(user_id)}
    value = {"$set": {"Cookie": cookie}}
    return user_records.update_one(query, value)


def fulfill_order(
    user_id,
    payer_id,
    order_id,
    transaction_id,
    units_purchased: int,
    gross: Decimal128,
    paypal_fee: Decimal128,
    net: Decimal128,
    first_name,
    last_name,
    email,
    create_time,
    timestamp
):
    query = {"_id": ObjectId(user_id)}
    value = {
        "$inc": {
            "Units": units_purchased,
            "UnitsPurchased": units_purchased,
            "TotalRevenue": gross
        },
        "$push": {
            "SalesRecords": {
                "OrderDetails": {
                    "TimeStamp": timestamp,
                    "PayPalOrderId": order_id,
                    "Units": units_purchased,
                    "PurchaseAmount": gross
                },
                "UserDetails": {
                    "PayPalPayerId": payer_id,
                    "FirstName": first_name,
                    "LastName": last_name,
                    "Email": email
                },
                "TransactionDetails": {
                    "PayPalTimeStamp": create_time,
                    "PayPalTransactionId": transaction_id,
                    "Gross": gross,
                    "PayPalFee": paypal_fee,
                    "Net": net
                }
            }
        }
    }
    return user_records.update_one(query, value)


def save_alert_data(user_id, twilio, timestamp):
    query = {"_id": ObjectId(user_id)}
    value = {
        "$inc": {
            "Units": -1,
            "UnitsSent": 1
        },
        "$push": {
            "TwilioRecords": {
                "Date": timestamp,
                "Type": "Alert",
                "Body": twilio.body,
                "Status": twilio.status,
                "ErrorMessage": twilio.error_message,
                "SID": twilio.sid
            }
        }
    }
    return user_records.update_one(query, value)


def get_all_user_data():
    return user_records.find()


def get_all_active_user_data():
    return user_records.find({"Units": {"$gt": 0}})


def get_active_user_data_by_subreddit(subreddit):
    return user_records.find({
        "Units": {"$gt": 0},
        "Subreddits": subreddit
    })


def get_user_data_by_id(user_id):
    return user_records.find_one({"_id": ObjectId(user_id)})


def get_user_data_by_order_id(order_id):
    return user_records.find_one({"SalesRecords.OrderDetails.PayPalOrderId": order_id})


def get_user_data_by_username(username):
    return user_records.find_one({"Username": username})


def get_user_data_by_phonenumber(ph):
    return user_records.find_one({"PhoneNumber": ph})


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


def add_subreddit(user_id, subreddit):
    query = {"_id": ObjectId(user_id)}
    value = {"$push": {"Subreddits": subreddit}}
    return user_records.update_one(query, value)


def delete_subreddit(user_id, subreddit):
    query = {"_id": ObjectId(user_id)}
    value = {"$pull": {"Subreddits": subreddit}}
    return user_records.update_one(query, value)


def reset_password(user_id, hashed_pw):
    query = {"_id": ObjectId(user_id)}
    value = {"$set": {"Password": hashed_pw}}
    return user_records.update_one(query, value)


def update_phonenumber(user_id, phonenumber):
    query = {"_id": ObjectId(user_id)}
    value = {"$set": {"PhoneNumber": phonenumber}}
    return user_records.update_one(query, value)


def update_username(user_id, new_username):
    query = {"_id": ObjectId(user_id)}
    value = {"$set": {"Username": new_username}}
    return user_records.update_one(query, value)


def get_subreddit_data():
    document = app_records.find_one({"Document": "REDDIT"})
    return document["Subreddits"]


def get_distinct_subreddit_names():
    return user_records.distinct("Subreddits")


def update_post_id(subreddit, post_id):
    query = {f"Subreddits.Subreddit": subreddit}
    value = {"$set": {
        "Subreddits.$.LastPostId": post_id
    }}
    return app_records.update_one(query, value, upsert=True)

