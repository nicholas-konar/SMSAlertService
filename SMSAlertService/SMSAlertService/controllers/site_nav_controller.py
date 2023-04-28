import markupsafe

from bcrypt import checkpw
from flask import Blueprint, request, redirect, render_template, session, url_for, jsonify
from twilio.base.exceptions import TwilioRestException
from SMSAlertService import app, mongo, alert_engine, util, config, twilio
from SMSAlertService.dao import DAO
from SMSAlertService.otp_service import OtpService

site_nav_bp = Blueprint('site_nav_controller', __name__)


@site_nav_bp.route("/", methods=["POST", "GET"])
def home():
    if "username" not in session:
        app.logger.info(f'Home accessed by unknown user')
        return render_template('home.html')
    else:
        username = session["username"]
        app.logger.info(f'User {username} viewed the homepage.')
        return render_template('home.html', username=username)


@site_nav_bp.route("/login", methods=["POST", "GET"])
def login():
    if "username" in session:
        return redirect(url_for("site_nav_controller.profile"))
    if request.method == "POST":
        username = markupsafe.escape(request.form.get("username").upper().strip())
        pw_input = markupsafe.escape(request.form.get("password"))
        user = DAO.get_user_by_username(username)

        if user is None:
            message = 'Incorrect username or password.'
            app.logger.error(f'Failed log in attempt: User {username} does not exist.')
            return render_template('login.html', message=message)

        if checkpw(pw_input.encode('utf-8'), user.password):
            session["username"] = user.username
            session["phonenumber"] = user.phonenumber
            if user.username == "ADMIN":
                session['ADMIN'] = True
                app.logger.info(f'User {user.username} logged in.')
                return redirect(url_for('admin_controller.admin'))
            else:
                if user.verified: # todo: unverified users can still log in. If the verification process is done correctly, we may not need this section at all.
                    app.logger.info(f'User {user.username} logged in.')
                    return redirect(url_for('site_nav_controller.profile'))
                else:
                    engine.process_otp(user)
                    app.logger.info(f'Unverified user {user.username} logged in. Redirecting to Account Confirmation page.')
                    return redirect(url_for('site_nav_controller.account_confirmation'))
        else:
            message = 'Incorrect username or password.'
            app.logger.error(f'Failed log in attempt: Incorrect password entered by {user.username}.')
            return render_template('login.html', message=message)

    return render_template('login.html')


@site_nav_bp.route("/logout", methods=["GET"])
def logout():
    username = session["username"]
    session.clear()
    app.logger.info(f'User {username} logged out.')
    return redirect(url_for("site_nav_controller.login"))


@site_nav_bp.route("/profile", methods=["GET"])
def profile():
    if username := session.get('username'):
        user = DAO.get_user_by_username(username)
        keywords = user.get_keywords_json()
        app.logger.info(f'User {username} viewed their profile.')
        return render_template('profile.html', message_count=user.units_left,
                               keywords=keywords, username=username, current_phone=user.phonenumber)
    else:
        return redirect(url_for("site_nav_controller.login"))


@site_nav_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if "username" in session:
        return redirect(url_for("site_nav_controller.profile"))

    if request.method == "GET":
        return render_template('signup.html')

    if request.method == "POST":
        username = markupsafe.escape(request.form.get("username").upper().strip())
        phonenumber = markupsafe.escape(request.form.get("phonenumber"))
        password = markupsafe.escape(request.form.get("password").strip())
        # todo: add checkbox for consent

        username_taken = mongo.username_taken(username)
        phonenumber_taken = mongo.phonenumber_taken(phonenumber)

        if username_taken:
            message = 'This username is already in use.'
            app.logger.info(f'Failed sign up attempt: Username {username} already in use')
            return render_template('signup.html', message=message)

        if phonenumber_taken:
            message = 'This phone number is already in use.'
            app.logger.info(f'Failed sign up attempt: Phone number {phonenumber} already in use')
            return render_template('signup.html', message=message)

        else:
            session["username"] = username
            session["phonenumber"] = phonenumber
            session["password"] = password
            app.logger.info(f'User {username} submitted a sign up form. ')
            return redirect(url_for('site_nav_controller.account_confirmation'))


@site_nav_bp.route("/account-confirmation", methods=["GET"])
def account_confirmation():
    if request.method == "GET":

        username = session["username"]
        phonenumber = session["phonenumber"]
        password = session["password"]

        try:
            otp = OtpService.generate_otp()
            twilio.send_otp(otp, phonenumber)
            session['otp'] = otp
            user = DAO.create_user(username, password, phonenumber)
            app.logger.info(f'User {username} signed up successfully')

        except TwilioRestException:
            mongo.drop_user(username)
            message = 'Invalid phone number.'
            app.logger.info(f'Failed account confirmation: TwilioRestException thrown by phone number {phonenumber}')
            return render_template('signup.html', message=message)

        return render_template('account-confirmation.html')


@site_nav_bp.route("/account-recovery", methods=["GET"])
def account_recovery():
    session['otpResends'] = 0
    session['otpAttempts'] = 0
    return render_template('account-recovery.html')


@site_nav_bp.route("/support", methods=["GET"])
def support():
    if "username" not in session:
        app.logger.info(f'Support page accessed by unknown user')
        return render_template('support.html')
    else:
        username = session["username"]
        app.logger.info(f'User {username} viewed the support page.')
        return render_template('support.html', username=username)


@site_nav_bp.route("/privacy", methods=["GET"])
def privacy():
    if "username" not in session:
        return render_template('privacy.html')
    else:
        username = session["username"]
        return render_template('privacy.html', username=username)


@site_nav_bp.route("/instructions", methods=["GET"])
def instructions():
    if "username" not in session:
        app.logger.info(f'Instructions accessed by unknown user')
        return render_template('instructions.html')
    else:
        username = session["username"]
        app.logger.info(f'User {username} viewed the instructions page.')
        return render_template('instructions.html', username=username)


@site_nav_bp.route("/edit-info", methods=["GET"])
def edit_info():
    username = session["username"]
    current_phone = session['phonenumber']
    app.logger.info(f'Edit info accessed by user {username}')
    return render_template('edit-info.html', username=username, current_phone=current_phone)


