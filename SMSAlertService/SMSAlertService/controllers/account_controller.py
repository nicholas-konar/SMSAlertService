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


@account_bp.route("/account/create", methods=["POST"])
@protected
def create():
    username = markupsafe.escape(request.json['Username'])
    ph = markupsafe.escape(request.json['Phonenumber'])
    pw = markupsafe.escape(request.json['Password'])
    verified = markupsafe.escape(request.json['Verified'])
    acknowledged = DAO.create_user(username=username, phonenumber=ph, password=pw, verified=verified)
    return jsonify({'Status': SUCCESS}) \
        if acknowledged else jsonify({'Status': FAIL, 'Message': FAIL_MSG})


@account_bp.route("/login", methods=["POST"])
def login():
    username = markupsafe.escape(request.json['Username'].upper().strip())
    pw_input = markupsafe.escape(request.json['Password'])
    user = DAO.get_user_by_username(username)
    app.logger.debug(f'checking user stuff during login')
    if user is None:
        app.logger.error(f'Failed log in attempt: User {username} does not exist.')
        return jsonify({'Status': FAIL, 'Message': INVALID_LOGIN_MSG})

    elif session['login_attempts'] >= MAX_LOGIN_ATTEMPTS or user.blocked:
        app.logger.debug(f'User {user.username} has exceeded max log in attempts.')
        DAO.block_user(user)
        return jsonify({'Status': BLOCKED, 'Message': BLOCKED_MSG})

    elif checkpw(pw_input.encode('utf-8'), user.password):
        app.logger.debug(f'Setting cookie...')
        cookie = secrets.token_hex(16)
        session["username"] = user.username
        session["phonenumber"] = user.phonenumber
        resp = jsonify({'Status': SUCCESS})
        resp.set_cookie('cookie', cookie, secure=True, httponly=True)
        DAO.set_cookie(user, cookie)
        return resp

    else:
        session['login_attempts'] += 1
        app.logger.error(f'Incorrect password entered by {user.username}. Login attempts = {session.get("login_attempts")}')
        return jsonify({'Status': FAIL, 'Message': INVALID_LOGIN_MSG})


@account_bp.route("/add-keyword", methods=["POST"])
@protected
def add_keyword():
    username = session.get('username')
    user = DAO.get_user_by_username(username)
    keyword = markupsafe.escape(request.json['keyword'].strip())
    success = DAO.add_keyword(user, keyword)
    return jsonify({'Status': SUCCESS}) \
        if success else jsonify({'Status': FAIL})


@account_bp.route("/delete-keyword", methods=["POST"])
@protected
def delete_keyword():
    username = session.get('username')
    user = DAO.get_user_by_username(username)
    keyword = markupsafe.escape(request.json['DeleteKeyword'])
    success = DAO.delete_keyword(user, keyword)
    return jsonify({'Status': SUCCESS}) \
        if success else jsonify({'Status': FAIL})


@account_bp.route("/delete-all-keywords", methods=["POST"])
@protected
def delete_all_keywords():
    username = session.get('username')
    user = DAO.get_user_by_username(username)
    success = DAO.delete_all_keywords(user)
    return jsonify({'Status': SUCCESS}) \
        if success else jsonify({'Status': FAIL})


@account_bp.route("/reset-password", methods=["POST"])
@protected
def reset_password():
    username = session['username']
    user = DAO.get_user_by_username(username)
    new_password = markupsafe.escape(request.json['NewPassword'])
    success = DAO.reset_password(user, new_password)
    return jsonify({'Status': SUCCESS, 'Message': PW_RESET_SUCCESS}) \
        if success else jsonify({'Status': FAIL, 'Message': FAIL_MSG})


@account_bp.route("account/update/username", methods=["POST"])
@protected
def update_username():
    old = session.get('username')
    new = markupsafe.escape(request.json['NewUsername'].upper())
    username_taken = mongo.username_taken(new)
    if username_taken:
        return jsonify({'Status': FAIL, 'Message': USERNAME_TAKEN_MSG})
    else:
        success = DAO.update_username(old, new)
        session["username"] = new
        return jsonify({'Status': SUCCESS})



