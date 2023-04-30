import markupsafe

from flask import Blueprint, request, redirect, render_template, session, url_for, jsonify
from SMSAlertService import app, mongo, alert_engine, util, config, twilio
from SMSAlertService.config import SUCCESS, FAIL, FAIL_MSG, PW_RESET_SUCCESS
from SMSAlertService.dao import DAO

account_bp = Blueprint('account_controller', __name__)


@account_bp.route("/add-keyword", methods=["POST"])
def add_keyword():
    if username := session.get('username'):
        user = DAO.get_user_by_username(username)
        keyword = markupsafe.escape(request.json['keyword'].strip())
        success = DAO.add_keyword(user, keyword)
        return jsonify({'Status': SUCCESS}) if success else jsonify({'Status': FAIL})
    else:
        return jsonify({'Status': FAIL})


@account_bp.route("/delete-keyword", methods=["POST"])
def delete_keyword():
    if username := session.get('username'):
        user = DAO.get_user_by_username(username)
        keyword = markupsafe.escape(request.json['DeleteKeyword'])
        success = DAO.delete_keyword(user, keyword)
        return jsonify({'Status': SUCCESS}) if success else jsonify({'Status': FAIL})
    else:
        return jsonify({'Status': FAIL})


@account_bp.route("/delete-all-keywords", methods=["POST"])
def delete_all_keywords():
    if username := session.get('username'):
        user = DAO.get_user_by_username(username)
        success = DAO.delete_all_keywords(user)
        return jsonify({'Status': SUCCESS}) if success else jsonify({'Status': FAIL})
    else:
        return jsonify({'Status': FAIL})


@account_bp.route("/promo-code", methods=["POST"])
def promo_code():
    username = session['username']
    code = request.form.get('promo-code')
    mongo.process_promo_code(username, code)
    return redirect(url_for("account"))


@account_bp.route("/reset-password", methods=["POST"])
def reset_password():
    if session.get('authenticated'):
        username = session['username']
        user = DAO.get_user_by_username(username)
        new_password = markupsafe.escape(request.json['NewPassword'])
        success = DAO.reset_password(user, new_password)
        if success:
            return jsonify({'Status': SUCCESS, 'Message': PW_RESET_SUCCESS})
        else:
            return jsonify({'Status': FAIL, 'Message': FAIL_MSG})
    else:
        return jsonify({'Status': FAIL, 'Message': FAIL_MSG})


@account_bp.route("/update-username", methods=["GET", "POST"])
def update_username():
    if "username" not in session:
        return redirect(url_for("index"))
    current_phone = session.get('phonenumber')
    old_username = session.get('username')
    if request.method == "GET":
        return render_template('edit-info.html', username=old_username,
                               current_phone=current_phone)
    elif request.method == "POST":
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


@account_bp.route("/update-phone-number", methods=["GET", "POST"])
def update_phone_number():
    if username := session.get('username'):
        new_number = request.form.get('newnumber')
        mongo.update_phonenumber(username, new_number)
        session['phonenumber'] = new_number
        message = 'Phone number updated successfully'
        return render_template('edit-info.html', message=message, username=username, current_phone=new_number)
    else:
        return redirect(url_for("index"))



