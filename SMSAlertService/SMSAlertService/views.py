import ssl

from bcrypt import checkpw
import pymongo
from flask import request, redirect, render_template, session, url_for, jsonify
from twilio.twiml.messaging_response import MessagingResponse

from SMSAlertService import app, mongo, notification

# PayPal
pp_access_token_DEV = 'A21AAIWQ8JmpLwLc98Dupzfy0A-xo2-o8YxK1d_C_XSf7HUG_C6GcjX0SidjaqvnoAtnZy-XNvSwV49AenLXUj1UdYuF14FWA'
pp_client_id_DEV = 'AcP7hzgEzQPWCWHLjdf-bndJwyxF59cjM7VYPk1rdOlSk6we6297xWyvsDuxALbNh_6er7t1AVuqzDsl'
pp_product_id_DEV = 'PROD-4N235400WD644974Y'
pp_plan_id_DEV = 'P-9F522710GA548083PMHL3TSY'
pp_subscription_link_DEV = 'https://www.paypal.com/webapps/billing/plans/subscribe?plan_id=P-33F52811MW323513PMHILFDA'

# Mongo SHOULD BE ABLE TO DELETE THIS AND KEEP IN MONGO.PY OR CONFIG FILE
import certifi

ca = certifi.where()

app.secret_key = "testing"
connection = "mongodb+srv://admin:6aQumg0BN557148F@cluster0.xwyrq.mongodb.net/test"
# client_DEV = pymongo.MongoClient(connection, tls=True, tlsAllowInvalidCertificates=True)
client_DEV = pymongo.MongoClient(connection)
db_DEV = client_DEV['gafs_alert_service_db']
user_records = db_DEV.user_data
app_records = db_DEV.app_data


# -------------------------------- ABOUT + LOGIN + LOGOUT + SIGNUP --------------------------------
@app.route("/", methods=["POST", "GET"])
def index():
    return render_template('index.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "username" in session:
        return redirect(url_for("profile"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        username_found = user_records.find_one({"Username": username})
        if username_found:
            passwordcheck = username_found['Password']

            if checkpw(password.encode('utf-8'), passwordcheck):
                session["username"] = username
                session["phonenumber"] = mongo.get_phonenumber(username_found['Username'])
                return redirect(url_for('profile'))
            else:
                # if "username" in session:
                #     return redirect(url_for("profile"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'The username "' + username + '" was not found in our records.'
            return render_template('index.html', message=message)
    return render_template('login.html', message=message)


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "username" in session:
        session.pop("username", None)
        session.pop("phonenumber", None)
        return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    message = 'Thank you for using the SMS Alert Service'
    if "username" in session:
        return redirect(url_for("profile"))
    if request.method == "POST":
        username = request.form.get("username")
        phonenumber = request.form.get("phonenumber")
        password = request.form.get("password")
        username_found = mongo.username_taken(username)
        if username_found:
            message = 'Username taken.'
            return render_template('signup.html', message=message)
        else:
            mongo.create_user(username, password, phonenumber)
            session["username"] = username
            session["phonenumber"] = phonenumber
            return redirect(url_for("profile", message=message, username=username, phonenumber=phonenumber))
    return render_template('signup.html')


@app.route("/about")
def about():
    return render_template('about.html')


# -------------------------------- PROFILE --------------------------------
@app.route('/profile')
def profile():
    if "username" not in session:
        return redirect(url_for("login"))
    else:
        username = session["username"]
        current_phone = session['phonenumber']
        message = 'SMS packages starting at $5.00!'
        message_count = mongo.get_message_count(username)

        return render_template('profile.html', message=message, message_count=message_count, username=username, current_phone=current_phone)


@app.route('/edit-info')
def edit_info():
    username = session["username"]
    current_phone = session['phonenumber']
    message = 'Edit Account Details'
    return render_template('edit-info.html', message=message, username=username, current_phone=current_phone)


# -------------------------------- PROFILE COMMANDS --------------------------------
@app.route("/update-username", methods=['GET', 'POST'])
def update_username():
    if "username" not in session:
        return redirect(url_for("index"))
    else:
        current_phone = session.get('phonenumber')
        old_username = session.get('username')
        new_username = request.form.get('newusername')
        username_taken = mongo.username_taken(new_username)
        if username_taken:
            message = 'Sorry, that username is taken.'
            return render_template('edit-info.html', message=message, username=old_username,
                                   current_phone=current_phone)
        else:
            mongo.update_username(old_username, new_username)
            session["username"] = new_username
            message = 'Username has been updated to ' + new_username
            return render_template('edit-info.html', message=message, username=new_username,
                                   current_phone=current_phone)


@app.route("/update-phone-number", methods=['GET', 'POST'])
def update_phone_number():
    if "username" not in session:
        return redirect(url_for("index"))
    else:
        username = session.get('username')
        new_number = request.form.get('newnumber')
        mongo.update_phonenumber(username, new_number)
        session['phonenumber'] = new_number
        message = 'Phone number updated successfully'
        return render_template('edit-info.html', message=message, username=username, current_phone=new_number,
                               )


@app.route("/add-keyword", methods=['GET', 'POST'])
def add_keyword():
    if "username" not in session:
        return redirect(url_for("login"))
    else:
        username = session.get('username')
        keyword = request.form.get('newkeyword')
        mongo.add_keyword(username, keyword)
        phonenumber = mongo.get_phonenumber(username)
        message_count = mongo.get_message_count(username)
        message = f'"{keyword}" has been added to keywords!'
        return render_template('profile.html', message=message, username=username, current_phone=phonenumber,
                               message_count=message_count)


@app.route("/delete-all-keywords", methods=['GET', 'POST'])
def delete_all_keywords():
    if "username" not in session:
        return redirect(url_for("login"))
    else:
        username = session.get('username')
        phonenumber = session.get('phonenumber')
        mongo.delete_all_keywords(username)
        message = 'All Keywords have been cleared.'
        message_count = mongo.get_message_count(username)
        app.logger.info(f'{username} cleared all keywords.')
        return redirect(url_for('profile', message=message,
                               username=username, current_phone=phonenumber,message_count=message_count))


# -------------------------------- PAYPAL WEBHOOKS --------------------------------
@app.route("/billing-subscription-created", methods=["POST", "GET"])
def webhook_billing_subscription_created():
    req = request.get_json()
    subscription = req['resource']['id']
    app.logger.debug('Billing subscription ' + subscription + ' was created.')
    return jsonify({"status": True})


@app.route("/billing-subscription-suspended", methods=["POST", "GET"])
def webhook_billing_subscription_suspended():
    req = request.get_json()
    subscription = req['resource']['id']
    app.logger.debug('Attempting to suspend SubscriptionId ' + subscription)
    mongo.suspend(subscription)
    return jsonify({"status": True})


@app.route("/billing-subscription-cancelled", methods=["POST", "GET"])
def webhook_billing_subscription_cancelled():
    req = request.get_json()
    subscription = req['resource']['id']
    app.logger.debug('Attempting to cancel SubscriptionId ' + subscription)
    mongo.deactivate(subscription)
    return jsonify({"status": True})


# -------------------------------- TWILLIO WEBHOOKS --------------------------------
@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    req = request.values
    body = req['Body']
    from_number = req['From']

    app.logger.debug('the body is as follows: ' + str(body))
    app.logger.debug('the from number is as follows: ' + str(from_number))

    if body.lower().startswith('reset password'):
        app.logger.debug('Password reset requested for ' + from_number)
        body = body.lower()
        password = body.split(' ')[2]
        mongo.reset_password(from_number, password)
        resp = MessagingResponse()
        resp.message("Your password has been reset. Thank you for using the GAFS Alert Service!")
        return str(resp)

    if body.lower().startswith("what's my username"):
        app.logger.debug('Username reminder requested for ' + from_number)
        # reply with username
        username = mongo.get_username_by_phonenumber(from_number)
        resp = MessagingResponse()
        resp.message(
            'The username associated with this number is ' + username + '. Thank you for using the GAFS Alert Service!')
        return str(resp)

    else:
        resp = MessagingResponse()
        resp.message(
            'I can respond to the following commands: \n"Reset password <newpassword>" \n"What\'s my username?"')
        return str(resp)


# -------------------------------- REDDIT WEBHOOKS --------------------------------
@app.route("/reddit-webhook", methods=['POST'])
def reddit_webhook():
    app.logger.debug('Reddit webhook POST request: ' + str(request.get_json()))
    notification.send()
    return jsonify({"status": True})


# -------------------------------- COMMANDS --------------------------------
@app.route("/process-sale")
def process_sale():
    username = session.get('username')
    status = request.args.get('status')
    units = request.args.get('units')
    amount = request.args.get('amount')

    app.logger.debug(f"status: {status}")
    app.logger.debug(f"units: {units}")
    app.logger.debug(f"Username: {username}")
    app.logger.debug(status is "COMPLETED")
    app.logger.debug(status == "COMPLETED")

    if status == "COMPLETED":
        mongo.process_transaction(username, units, amount)
        return redirect(url_for("profile"))
    else:
        return jsonify({"status": False})


@app.route("/notify", methods=['GET'])
def notify():
    resp = notification.send()
    # return jsonify(resp)
    return resp


# link username & subscriptionID from js pp button
@app.route('/record-subscription-id')
def record_subscription_id():
    username = request.args.get('username')
    subscription_id = request.args.get('id')
    mongo.activate_subscription(username, subscription_id)
    return jsonify({"status": True})
