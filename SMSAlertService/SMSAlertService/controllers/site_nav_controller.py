import markupsafe
from flask import Blueprint, request, redirect, render_template, session, url_for

from SMSAlertService import app, mongo
from SMSAlertService.dao import DAO
from SMSAlertService.decorators import protected

site_nav_bp = Blueprint('site_nav_controller', __name__)


@site_nav_bp.route("/", methods=["POST", "GET"])
def home():
    return render_template('home.html')


@site_nav_bp.route("/login", methods=["GET"])
def login():
    if 'login_attempts' not in session:
        session['login_attempts'] = 0
    return render_template('login.html')


@site_nav_bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("site_nav_controller.login"))


@site_nav_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if "username" in session:
        return redirect(url_for("site_nav_controller.account"))

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
@protected
def edit_info():
    username = session["username"]
    current_phone = session['phonenumber']
    app.logger.info(f'Edit info accessed by user {username}')
    return render_template('edit-info.html', username=username, current_phone=current_phone)


