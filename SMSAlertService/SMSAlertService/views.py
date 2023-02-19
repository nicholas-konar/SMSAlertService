from bcrypt import checkpw
from flask import request, redirect, render_template, session, url_for, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.base.exceptions import TwilioRestException

from SMSAlertService import app, mongo, engine, util, twilio


# -------------------------------- ABOUT + LOGIN + LOGOUT + SIGNUP --------------------------------
@app.route("/", methods=["POST", "GET"])
def home():
    if "username" not in session:
        app.logger.info(f'Home accessed by unknown user')
        return render_template('home.html')
    else:
        username = session["username"]
        app.logger.info(f'Home accessed by {username}')
        return render_template('home.html', username=username)


@app.route("/support")
def support():
    if "username" not in session:
        app.logger.info(f'Support page accessed by unknown user')
        return render_template('support.html')
    else:
        username = session["username"]
        app.logger.info(f'Support page accessed by {username}')
        return render_template('support.html', username=username)


@app.route("/privacy")
def privacy():
    if "username" not in session:
        return render_template('privacy.html')
    else:
        username = session["username"]
        return render_template('privacy.html', username=username)


@app.route("/instructions")
def instructions():
    if "username" not in session:
        app.logger.info(f'Instructions accessed by unknown user')
        return render_template('instructions.html')
    else:
        username = session["username"]
        app.logger.info(f'Instructions accessed by {username}')
        return render_template('instructions.html', username=username)


@app.route("/login", methods=["POST", "GET"])
def login():
    if "username" in session:
        return redirect(url_for("profile"))
    if request.method == "POST":
        username = request.form.get("username").upper().strip()
        pw_input = request.form.get("password")
        user = mongo.get_user_by_username(username)
        if user:
            password = user['Password']
            if checkpw(pw_input.encode('utf-8'), password):
                session["username"] = user['Username']
                session["phonenumber"] = user['PhoneNumber']
                if user['Username'] == "ADMIN":
                    session['ADMIN'] = True
                    app.logger.info(f'User {username} logged in')
                    return redirect(url_for('admin'))
                app.logger.info(f'User {username} logged in')
                return redirect(url_for('profile'))
            else:
                message = 'Incorrect password.'
                app.logger.info(f'Failed log in attempt: Incorrect password entered by {username}')
                return render_template('login.html', message=message)
        else:
            message = 'User not found.'
            app.logger.info(f'Failed log in attempt: User {username} not found')
            return render_template('login.html', message=message)
    return render_template('login.html')


@app.route("/logout", methods=["POST", "GET"])
def logout():
    username = session["username"]
    session.clear()
    app.logger.info(f'User {username} logged out')
    return redirect(url_for("login"))


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if "username" in session:
        return redirect(url_for("profile"))

    if request.method == "POST":
        username = request.form.get("username").upper().strip()
        phonenumber = request.form.get("phonenumber")
        password = request.form.get("password").strip()

        username_taken = mongo.username_taken(username)
        phonenumber_taken = mongo.phonenumber_taken(phonenumber)

        if username_taken:
            message = 'Username taken.'
            app.logger.info(f'Failed sign up attempt: Username {username} already in use')
            return render_template('signup.html', message=message)

        if phonenumber_taken:
            message = 'This phone number is already in use. If you need to reset your password, go to the login page.'
            app.logger.info(f'Failed sign up attempt: Phone number {phonenumber} already in use')
            return render_template('signup.html', message=message)

        else:
            try:
                mongo.create_user(username, password, phonenumber)
                engine.process_otp(phonenumber)  # for account confirmation
                session["username"] = username
                session["phonenumber"] = phonenumber
                app.logger.info(f'User {username} signed up successfully')
                return redirect(url_for('account_confirmation'))

            except TwilioRestException:
                # Todo: refine the failed confirmation process
                message = 'We are unable to reach this phone number. ' \
                          'Please send your phone number and username to support@smsalertservice.com and we\'ll fix it promptly.'
                app.logger.info(f'Failed phone number confirmation: TwilioRestException thrown by phone number {phonenumber}')
                # Todo: build account-confirmation-retry.html
                return render_template('profile.html', message=message)

    app.logger.info(f'Sign up page accessed by unknown user')
    return render_template('signup.html')


@app.route("/account-confirmation", methods=['GET', 'POST'])
def account_confirmation():
    if request.method == 'GET':
        app.logger.info('Rendering account confirmation page')
        return render_template('account-confirmation.html')


# -------------------------------- PROFILE --------------------------------
@app.route('/admin')
def admin():
    if session["ADMIN"]:
        username = session["username"]
        users = mongo.get_user_data()
        total_users = len(users)
        total_units_sent = util.calculate_total_units_sent(users)
        total_units_sold = util.calculate_total_units_sold(users)
        total_revenue = util.calculate_total_revenue(users)
        total_codes_redeemed = util.calculate_total_codes_redeemed(users)

        codes = mongo.get_codes()
        total_codes = util.calculate_issued_codes(codes)
        active_codes = util.calculate_total_active_codes(codes)

        app.logger.info(f'***ADMIN PAGE ACCESSED BY {username}')
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
        app.logger.info(f'User {username} accessed their profile')
        return render_template('profile.html', message_count=message_count,
                               keywords=keywords, username=username, current_phone=current_phone)


@app.route('/edit-info')
def edit_info():
    username = session["username"]
    current_phone = session['phonenumber']
    app.logger.info(f'Edit info accessed by user {username}')
    return render_template('edit-info.html', username=username, current_phone=current_phone)


@app.route('/account-recovery')
def account_recovery():
    app.logger.info(f'Account recovery accessed by unknown user')
    return render_template('account-recovery.html')


@app.route('/send/<path>', methods=['POST'])
def send(path):
    ph = request.form.get('PhoneNumber')
    try:
        engine.process_otp(ph)
        session['phonenumber'] = ph
        if path == 'account-verification':
            return render_template('account-verification.html')
    except TwilioRestException:
        if path == 'account-verification':
            app.logger.info(f'Failed OTP delivery attempt: TwilioRestException for phone number {ph}')
            return render_template('account-recovery.html', message='There are no accounts associated with that number.')


@app.route('/resend/<path>', methods=['POST'])
def resend(path):
    username = session['username']
    ph = session['phonenumber']
    app.logger.info(f'Attempting resend for {username}')
    engine.process_otp(ph)
    return render_template(f'{path}.html', sent=True)


@app.route('/authenticate/<path>', methods=['POST'])
def authenticate(path):
    if request.method == 'POST':
        ph = session['phonenumber']
        user = mongo.get_user_by_phonenumber(ph)
        username = user['Username']
        otp = request.form.get('otp')
        authenticated = util.authenticate(ph, otp)
        if authenticated and path == 'account-confirmation':
            mongo.verify(username)
            return redirect(url_for('profile'))
        if authenticated and path == 'account-verification':
            mongo.verify(username)
            return redirect(url_for('reset_password'))
        elif not authenticated:
            message = "Invalid code."
            return render_template(f'{path}.html', message=message)
    return render_template(f'{path}.html')


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'GET':
        return render_template('reset-password.html')
    if request.method == 'POST':
        ph = session['phonenumber']
        username = mongo.get_user_by_phonenumber(ph)
        pw = request.form.get('password')
        mongo.reset_password(username, pw)
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
    current_phone = session.get('phonenumber')
    old_username = session.get('username')
    if request.method == 'GET':
        return render_template('edit-info.html', username=old_username,
                               current_phone=current_phone)
    elif request.method == 'POST':
        new_username = request.form.get('newusername').upper()
        username_taken = mongo.username_taken(new_username)
        if username_taken:
            return render_template('edit-info.html', failed=True, username=old_username,
                                   current_phone=current_phone)
        else:
            mongo.update_username(old_username, new_username)
            session["username"] = new_username
            return render_template('edit-info.html', success=True, username=new_username,
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
        keyword = request.form.get('newkeyword').strip()
        mongo.add_keyword(username, keyword)
        return redirect(url_for('profile'))


@app.route("/delete-keyword", methods=['POST'])
def delete_keyword():
    if "username" not in session:
        return redirect(url_for("login"))
    else:
        username = session.get('username')
        keyword = request.values.get('keyword')
        mongo.delete_keyword(username, keyword)
        return redirect(url_for('profile'))


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
        return redirect(url_for('profile', message=message,
                                username=username, current_phone=phonenumber, message_count=message_count))


# -------------------------------- COMMANDS --------------------------------
@app.route("/process-sale")
def process_sale():
    username = session.get('username')
    status = request.args.get('status')
    units = request.args.get('units')
    amount = request.args.get('amount')
    app.logger.info(f'Processing sale of {units} units to user {username} for ${amount} - status: {status}')
    if status == "COMPLETED":
        mongo.process_transaction(username, units, amount)
        return redirect(url_for("profile"))
    else:
        return jsonify({"status": False})


@app.route("/notify", methods=['GET'])
def notify():
    resp = engine.run()
    return resp


@app.route("/generate-codes", methods=['POST'])
def generate_codes():
    # /generate-codes?reward=10&batch_size=5&distributor=Chad&prefix=nk
    # http://127.0.0.1:5000/generate-codes?reward=10&batch_size=1&distributor=Chad&prefix=nk
    if session["ADMIN"]:
        reward = request.form.get('reward')
        quantity = request.form.get('quantity')
        distributor = request.form.get('distributor')
        prefix = request.form.get('prefix')
        mongo.create_promo_codes(reward, quantity, distributor, prefix)
        return redirect(url_for('admin'))
    else:
        return None
