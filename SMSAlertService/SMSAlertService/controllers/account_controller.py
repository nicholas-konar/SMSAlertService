import secrets

import markupsafe

from bcrypt import checkpw
from flask import Blueprint, request, redirect, render_template, session, url_for, jsonify
from SMSAlertService import app, mongo, alert_engine, util, config, twilio
from SMSAlertService.config import SUCCESS, FAIL, FAIL_MSG, PW_RESET_SUCCESS, INVALID_LOGIN_MSG, MAX_LOGIN_ATTEMPTS, \
    BLOCKED, BLOCKED_MSG, USERNAME_TAKEN_MSG
from SMSAlertService.dao import DAO
from SMSAlertService.decorators import protected

account_bp = Blueprint('account_controller', __name__)


@protected
@account_bp.route("/account", methods=["GET"])
def account():
    user_id = session.get('user_id')
    user = DAO.get_user(user_id)
    keywords = user.get_keywords_json()
    app.logger.info(f'User {user.username} viewed their account.')
    return render_template('account.html', message_count=user.units_left,
                           keywords=keywords, username=user.username, current_phone=user.phonenumber)


@account_bp.route("/account/login", methods=["POST"])
def login():
    username = markupsafe.escape(request.json['Username'].upper().strip())
    pw_input = markupsafe.escape(request.json['Password'])
    user = DAO.get_user_by_username(username)

    if user is None:
        app.logger.error(f'Failed log in attempt: User {username} does not exist.')
        return jsonify({'Status': FAIL, 'Message': INVALID_LOGIN_MSG})

    elif session['login_attempts'] >= MAX_LOGIN_ATTEMPTS or user.blocked:
        app.logger.debug(f'User {user.username} has exceeded max log in attempts.')
        DAO.block_user(user)
        return jsonify({'Status': BLOCKED, 'Message': BLOCKED_MSG})

    elif checkpw(pw_input.encode('utf-8'), user.password):
        token = secrets.token_hex(16)
        session['token'] = token
        session['user_id'] = user.id
        session['username'] = user.username
        session['phonenumber'] = user.phonenumber
        DAO.set_cookie(user, token)
        resp = jsonify({'Status': SUCCESS})
        resp.set_cookie('sms_alert_service_login', value=token, secure=True, httponly=True)
        return resp

    else:
        session['login_attempts'] += 1
        app.logger.error(f'Incorrect password entered by {user.username}. Login attempts = {session.get("login_attempts")}')
        return jsonify({'Status': FAIL, 'Message': INVALID_LOGIN_MSG})


@account_bp.route("/account/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("site_nav_controller.login"))


@protected
@account_bp.route("/account/create", methods=["POST"])
def create():
    username = markupsafe.escape(request.json['Username'])
    ph = markupsafe.escape(request.json['Phonenumber'])
    pw = markupsafe.escape(request.json['Password'])
    verified = markupsafe.escape(request.json['Verified'])
    acknowledged = DAO.create_user(username=username, phonenumber=ph, password=pw, verified=verified)
    user = DAO.get_user_by_username(username)
    session['user_id'] = user.id
    return jsonify({'Status': SUCCESS}) \
        if acknowledged else jsonify({'Status': FAIL, 'Message': FAIL_MSG})


@protected
@account_bp.route("/account/update", methods=["GET"])
def edit_info():
    username = session["username"]
    current_phone = session['phonenumber']
    return render_template('edit-info.html', username=username, current_phone=current_phone)


@protected
@account_bp.route("/account/update/username", methods=["POST"])
def update_username():
    old = session.get('username')
    new = markupsafe.escape(request.json['NewUsername'].upper())
    username_taken = mongo.username_taken(new)
    if username_taken:
        return jsonify({'Status': FAIL, 'Message': USERNAME_TAKEN_MSG})
    else:
        success = DAO.update_username(old, new)
        session["username"] = new
        return jsonify({'Status': SUCCESS}) if success else jsonify({'Status': FAIL, 'Message': FAIL_MSG})


@protected
@account_bp.route("/account/update/password", methods=["POST"])
def reset_password():
    username = session['username']
    user = DAO.get_user_by_username(username)
    new_password = markupsafe.escape(request.json['NewPassword'])
    success = DAO.reset_password(user, new_password)
    return jsonify({'Status': SUCCESS, 'Message': PW_RESET_SUCCESS}) \
        if success else jsonify({'Status': FAIL, 'Message': FAIL_MSG})


@account_bp.route("/account/recover", methods=["GET"])
def recover_account():
    session['otp_resends'] = 0
    session['otp_attempts'] = 0
    return render_template('reset-password.html')


@protected
@account_bp.route("/account/keyword/add", methods=["POST"])
def add_keyword():
    username = session.get('username')
    user = DAO.get_user_by_username(username)
    keyword = markupsafe.escape(request.json['keyword'].strip())
    success = DAO.add_keyword(user, keyword)
    return jsonify({'Status': SUCCESS}) \
        if success else jsonify({'Status': FAIL})


@protected
@account_bp.route("/account/keyword/delete", methods=["POST"])
def delete_keyword():
    username = session.get('username')
    user = DAO.get_user_by_username(username)
    keyword = markupsafe.escape(request.json['DeleteKeyword'])
    success = DAO.delete_keyword(user, keyword)
    return jsonify({'Status': SUCCESS}) \
        if success else jsonify({'Status': FAIL})


@protected
@account_bp.route("/account/keyword/delete/all", methods=["POST"])
def delete_all_keywords():
    username = session.get('username')
    user = DAO.get_user_by_username(username)
    success = DAO.delete_all_keywords(user)
    return jsonify({'Status': SUCCESS}) \
        if success else jsonify({'Status': FAIL})


