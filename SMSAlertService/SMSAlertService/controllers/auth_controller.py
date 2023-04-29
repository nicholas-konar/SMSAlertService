import markupsafe

from flask import Blueprint
from flask import request, redirect, render_template, session, url_for, jsonify
from twilio.base.exceptions import TwilioRestException
from SMSAlertService import app, config, util
from SMSAlertService.dao import DAO
from SMSAlertService.otp_service import OtpService
from SMSAlertService.config import MAX_RESENDS, BLOCKED, BLOCKED_MSG, MAX_ATTEMPTS, RESEND_MSG, ERROR_MSG, FAIL, \
    RETRY_MSG, SUCCESS, FAIL_MSG, ERROR, INVALID_PH_MSG, AUTHENTICATED

auth_bp = Blueprint('auth_controller', __name__)


@auth_bp.route("/modal/authenticate", methods=["GET"])
def challenge():
    session['otp_resends'] = 0
    session['otp_attempts'] = 0
    return render_template('modal/authenticate.html')


@auth_bp.route("/send/otp", methods=["POST"])
def send():
    ph = markupsafe.escape(request.json['PhoneNumber'])
    flow_type = request.json['FlowType']

    if not util.is_valid_phone_number(ph):
        return jsonify({'Status': FAIL, 'Message': INVALID_PH_MSG})

    if (user := DAO.get_user_by_phonenumber(ph)) is None:
        return jsonify({'Status': FAIL, 'Message': INVALID_PH_MSG})

    elif session.get('otp_resends') >= MAX_RESENDS or user.blocked:
        app.logger.info(f'User {user.username} exceeded max OTP resends.')
        DAO.block_user(user)
        return jsonify({'Status': BLOCKED, 'Message': BLOCKED_MSG})

    else:
        try:
            otp = OtpService.generate_otp()
            # status = OtpService.send_otp(otp, user.phonenumber) #todo: uncomment after testing
            app.logger.debug(f'Sending OTP to {user.username}. Resends = {session["otp_resends"]}.')
            session['username'] = user.username
            session['phonenumber'] = user.phonenumber
            session['otp_resends'] += 1
            app.logger.debug(f'Resend count = {session["otp_resends"]}')
            session['otp'] = otp
            return jsonify({'Status': SUCCESS, 'FlowType': flow_type})

        except TwilioRestException:
            app.logger.info(f'OTP delivery error: TwilioRestException for phone number {ph}')
            return jsonify({'Success': ERROR, 'Message': ERROR_MSG})


@auth_bp.route("/resend/otp", methods=["POST"])
def resend():
    ph = session.get('phonenumber')
    user = DAO.get_user_by_phonenumber(ph)
    app.logger.info(f'Processing OTP resend request by {user.username}.')
    if user.blocked:
        app.logger.info(f'Denied OTP resend to user {user.username}: Blocked status is {user.blocked}.')
        return jsonify({'Status': BLOCKED, 'Message': BLOCKED_MSG})

    elif session.get('otp_resends') > MAX_RESENDS:
        app.logger.info(f'Max resends limit reached. Blocking user {user.username}')
        DAO.block_user(user)
        return jsonify({'Status': BLOCKED, 'Message': BLOCKED_MSG})

    else:
        try:
            otp = OtpService.generate_otp()
            # status = OtpService.send_otp(otp, user.phonenumber) #todo: uncomment after testing
            app.logger.debug(f'Resending OTP to {user.username}. Resends = {session["otp_resends"]}.')
            session['username'] = user.username
            session['phonenumber'] = user.phonenumber
            session['otp_resends'] += 1
            session['otp'] = otp
            return jsonify({'Status': SUCCESS, 'Message': RESEND_MSG})

        except TwilioRestException:
            app.logger.info(f'OTP delivery error: TwilioRestException for phone number {ph}')
            return jsonify({'Success': ERROR, 'Message': ERROR_MSG})


@auth_bp.route("/validate/otp", methods=["POST"])
def validate():
    expected = session.get('otp')
    actual = markupsafe.escape(request.json['OTP'])
    authenticated = OtpService.authenticate_otp(expected, actual)

    username = session.get('username')
    user = DAO.get_user_by_username(username)

    if session.get('otp_attempts') >= MAX_ATTEMPTS or user.blocked:
        DAO.block_user(user)
        return jsonify({'Status': BLOCKED, 'Message': BLOCKED_MSG})

    if authenticated:
        session['authenticated'] = True
        app.logger.info(f'User {user.username} has been authenticated.')
        if not user.verified:
            DAO.verify_user(user)
        return jsonify({'Status': AUTHENTICATED})
    else:
        session['otp_attempts'] += 1
        app.logger.error(f'User {user.username} failed authentication {session.get("otp_attempts")} time(s).')
        return jsonify({'Status': FAIL, 'Message': RETRY_MSG})

