from bcrypt import checkpw
from flask import request, redirect, render_template, session, url_for, jsonify
from twilio.twiml.messaging_response import MessagingResponse

from SMSAlertService import app, mongo, notification, util


# -------------------------------- ABOUT + LOGIN + LOGOUT + SIGNUP --------------------------------
@app.route("/", methods=["POST", "GET"])
def home():
    if "username" not in session:
        return render_template('home.html')
    else:
        username = session["username"]
        return render_template('home.html', username=username)


@app.route("/contact")
def contact():
    if "username" not in session:
        return render_template('contact.html')
    else:
        username = session["username"]
        return render_template('contact.html', username=username)


@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "username" in session:
        return redirect(url_for("profile"))

    if request.method == "POST":
        username = request.form.get("username")
        pw_input = request.form.get("password")
        user = mongo.get_user_by_username(username)
        if user:
            password = user['Password']
            if checkpw(pw_input.encode('utf-8'), password):
                session["username"] = user['Username']
                session["phonenumber"] = user['PhoneNumber']
                if user['Username'] == "Admin":
                    session['admin'] = True
                    return redirect(url_for('admin'))
                return redirect(url_for('profile'))
            else:
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'The username "' + username + '" was not found in our records.'
            return render_template('index.html', message=message)
    return render_template('login.html', message=message)


@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    return redirect(url_for("login"))


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


# -------------------------------- PROFILE --------------------------------
@app.route('/admin')
def admin():
    if "admin" in session:
        users = mongo.get_users()
        total_users = len(users)
        total_units_sent = util.calculate_total_units_sent(users)
        total_units_sold = util.calculate_total_units_sold(users)
        total_revenue = util.calculate_total_revenue(users)
        total_codes_redeemed = util.calculate_total_codes_redeemed(users)

        codes = mongo.get_codes()
        total_codes = util.calculate_issued_codes(codes)
        active_codes = util.calculate_total_active_codes(codes)

        return render_template('admin.html', username=True, total_users=total_users, total_codes=total_codes,
                               active_codes=active_codes, total_revenue=total_revenue,
                               total_units_sent=total_units_sent, total_units_sold=total_units_sold,
                               total_codes_redeemed=total_codes_redeemed)
    else:
        return redirect(url_for("login"))


@app.route('/profile')
def profile():
    if "username" not in session:
        return redirect(url_for("login"))
    else:
        username = session["username"]
        current_phone = session['phonenumber']
        user = mongo.get_user_by_username(username)
        message_count = user['Units']
        keywords = user['Keywords']
        return render_template('profile.html', message_count=message_count,
                               keywords=keywords, username=username, current_phone=current_phone)


@app.route('/edit-info')
def edit_info():
    username = session["username"]
    current_phone = session['phonenumber']
    return render_template('edit-info.html', username=username, current_phone=current_phone)


@app.route('/account-recovery')
def account_recovery():
    return render_template('account-recovery.html')


@app.route('/send', methods=['POST'])
def send():
    ph = request.form.get('PhoneNumber')
    session['phonenumber'] = ph
    notification.send_otp(ph)
    return redirect(url_for('authenticate'))


@app.route('/resend', methods=['POST'])
def resend():
    ph = session['phonenumber']
    notification.send_otp(ph)
    return render_template('authenticate.html', sent=True)


@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    if request.method == 'POST':
        ph = session['phonenumber']
        otp = request.form.get('otp')
        authenticated = util.authenticate(ph, otp)
        if authenticated:
            return redirect(url_for('reset_password'))
        else:
            message = "Incorrect OTP."
            return render_template('authenticate.html', message=message)
    return render_template('authenticate.html')


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'GET':
        return render_template('reset-password.html')
    if request.method == 'POST':
        ph = session['phonenumber']
        pw = request.form.get('password')
        mongo.reset_password(ph, pw)
        return redirect(url_for('login'))


@app.route('/promo-code', methods=['POST'])
def promo_code():
    username = session['username']
    code = request.form.get('promo-code')
    mongo.process_promo_code(username, code)
    return redirect(url_for("profile"))


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
        keywords = mongo.get_keywords(username)
        return redirect(url_for('profile', message=message, username=username, current_phone=phonenumber,
                                keywords=keywords, message_count=message_count))


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
                                username=username, current_phone=phonenumber, message_count=message_count))


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
    notification.distribute()
    return jsonify({"status": True})


# -------------------------------- COMMANDS --------------------------------
@app.route("/process-sale")
def process_sale():
    username = session.get('username')
    status = request.args.get('status')
    units = request.args.get('units')
    amount = request.args.get('amount')
    if status == "COMPLETED":
        mongo.process_transaction(username, units, amount)
        return redirect(url_for("profile"))
    else:
        return jsonify({"status": False})


@app.route("/notify", methods=['GET'])
def notify():
    resp = notification.distribute()
    return resp


@app.route("/generate-codes", methods=['POST'])
def generate_codes():
    # /generate-codes?reward=10&batch_size=5&distributor=Chad&prefix=nk
    # http://127.0.0.1:5000/generate-codes?reward=10&batch_size=1&distributor=Chad&prefix=nk
    if 'admin' in session:
        reward = request.form.get('reward')
        quantity = request.form.get('quantity')
        distributor = request.form.get('distributor')
        prefix = request.form.get('prefix')
        mongo.create_promo_codes(reward, quantity, distributor, prefix)
        return redirect(url_for('admin'))
    else:
        return None
