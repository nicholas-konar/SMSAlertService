import secrets

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
def authenticate():
    session['otp_resends'] = 0
    session['otp_attempts'] = 0
    return render_template('modal/authenticate.html')


@auth_bp.route("/account/create/send/otp", methods=["POST"])
def send_to_create():
    flow_type = request.json['FlowType']
    ph = markupsafe.escape(request.json['PhoneNumber'])

    if session.get('otp_resends') >= MAX_RESENDS:
        return jsonify({'Status': BLOCKED, 'Message': BLOCKED_MSG})

    try:
        otp = OtpService.generate_otp()
        # status = OtpService.send_otp(otp, user.phonenumber) # todo: uncomment after testing
        app.logger.info(f'Sending OTP to prospective user at {ph}. Resends = {session["otp_resends"]}.')
        session['otp_resends'] += 1
        session['otp'] = otp # todo: should probably make this more secure
        return jsonify({'Status': SUCCESS, 'FlowType': flow_type})

    except TwilioRestException:
        app.logger.info(f'OTP delivery error: TwilioRestException for phone number {ph}')
        return jsonify({'Success': ERROR, 'Message': ERROR_MSG})


@auth_bp.route("/account/create/resend/otp", methods=["POST"])
def resend_to_create():
    # this is mostly a copy of send(). Consider combining to one method with additional logic for resend handling.
    # the main differences are including a resend 'Message' in the response (shown in browser) and logging.
    flow_type = request.json['FlowType']
    ph = markupsafe.escape(request.json['PhoneNumber'])

    if session.get('otp_resends') >= MAX_RESENDS:
        return jsonify({'Status': BLOCKED, 'Message': BLOCKED_MSG})

    try:
        otp = OtpService.generate_otp()
        # status = OtpService.send_otp(otp, user.phonenumber) # todo: uncomment after testing
        app.logger.info(f'Sending OTP to prospective user at {ph}. Resends = {session["otp_resends"]}.')
        session['otp_resends'] += 1
        session['otp'] = otp # todo: should probably make this more secure
        return jsonify({'Status': SUCCESS, 'FlowType': flow_type, 'Message': RESEND_MSG})

    except TwilioRestException:
        app.logger.info(f'OTP delivery error: TwilioRestException for phone number {ph}')
        return jsonify({'Success': ERROR, 'Message': ERROR_MSG})


@auth_bp.route("/account/create/validate/otp", methods=["POST"])
def validate_to_create():
    flow_type = request.json['FlowType']
    expected = session.get('otp')  # todo: this could allow attackers to spoof session and gain access to any account
    actual = markupsafe.escape(request.json['OTP']) # todo: send expected otp through each request along with FlowType.
    authenticated = OtpService.authenticate_otp(expected, actual)

    if session.get('otp_attempts') >= MAX_ATTEMPTS:
        app.logger.info(f'Max attempts limit (in session only) reached by prospective user. Denied resend.')
        return jsonify({'Status': BLOCKED, 'Message': BLOCKED_MSG})

    if authenticated:
        app.logger.info(f'Prospective user has been authenticated.')
        return jsonify({'Status': AUTHENTICATED, 'FlowType': flow_type})

    else:
        session['otp_attempts'] += 1
        app.logger.error(f'Prospective user failed authentication {session.get("otp_attempts")} time(s).')
        return jsonify({'Status': FAIL, 'Message': RETRY_MSG})


@auth_bp.route("/account/create/validate/credentials", methods=["POST"])
def validate_credentials():
    username = markupsafe.escape(request.json['Username'])
    ph = markupsafe.escape(request.json['PhoneNumber'])
    credential_availability = DAO.get_credential_availability(username, ph)
    return jsonify({'CredentialAvailability': credential_availability})


@auth_bp.route("/account/recover/send/otp", methods=["POST"])
def send_to_recover():
    ph = markupsafe.escape(request.json['PhoneNumber'])
    flow_type = request.json['FlowType']

    if not util.is_valid_phone_number(ph):
        return jsonify({'Status': FAIL, 'Message': INVALID_PH_MSG})

    if (user := DAO.get_user_by_phonenumber(ph)) is None:
        return jsonify({'Status': FAIL, 'Message': INVALID_PH_MSG})

    if session.get('otp_resends') >= MAX_RESENDS or user.blocked:
        app.logger.info(f'{user.username} exceeded max OTP resends.')
        DAO.block_user(user)
        return jsonify({'Status': BLOCKED, 'Message': BLOCKED_MSG})

    try:
        otp = OtpService.generate_otp()
        # status = OtpService.send_otp(otp, user.phonenumber) #todo: uncomment after testing
        app.logger.debug(f'Sending OTP to {user.username}. Resends = {session["otp_resends"]}.')
        session['username'] = user.username
        session['phonenumber'] = user.phonenumber
        session['otp_resends'] += 1
        session['otp'] = otp
        return jsonify({'Status': SUCCESS, 'FlowType': flow_type})

    except TwilioRestException:
        app.logger.info(f'OTP delivery error: TwilioRestException for phone number {ph}')
        return jsonify({'Success': ERROR, 'Message': ERROR_MSG})


@auth_bp.route("/account/recover/resend/otp", methods=["POST"])
def resend_to_recover():
    flow_type = request.json['FlowType']
    ph = session.get('phonenumber')
    user = DAO.get_user_by_phonenumber(ph)
    app.logger.info(f'OTP resend requested by {user.username}.')

    if user.blocked:
        app.logger.info(f'Denied OTP resend to user {user.username}: Blocked status is {user.blocked}.')
        return jsonify({'Status': BLOCKED, 'Message': BLOCKED_MSG})

    if session.get('otp_resends') > MAX_RESENDS:
        app.logger.info(f'Max resends limit reached. Blocking {user.username}.')
        DAO.block_user(user)
        return jsonify({'Status': BLOCKED, 'Message': BLOCKED_MSG})

    try:
        otp = OtpService.generate_otp()
        # status = OtpService.send_otp(otp, user.phonenumber) #todo: uncomment after testing
        app.logger.debug(f'Resending OTP to {user.username}. Resends = {session["otp_resends"]}.')
        session['username'] = user.username
        session['phonenumber'] = user.phonenumber
        session['otp_resends'] += 1
        session['otp'] = otp
        return jsonify({'Status': SUCCESS, 'FlowType': flow_type, 'Message': RESEND_MSG})

    except TwilioRestException:
        app.logger.info(f'OTP delivery error: TwilioRestException for phone number {ph}.')
        return jsonify({'Success': ERROR, 'Message': ERROR_MSG})


@auth_bp.route("/account/recover/validate/otp", methods=["POST"])
def validate_to_recover():
    flow_type = request.json['FlowType']
    expected = session.get('otp') # todo: this could allow attackers to spoof session and gain access to any account
    actual = markupsafe.escape(request.json['OTP'])
    authenticated = OtpService.authenticate_otp(expected, actual)

    username = session.get('username')
    user = DAO.get_user_by_username(username)

    if session.get('otp_attempts') >= MAX_ATTEMPTS or user.blocked:
        app.logger.info(f'Max attempts limit reached. Blocking user {user.username}')
        DAO.block_user(user)
        return jsonify({'Status': BLOCKED, 'Message': BLOCKED_MSG})

    if authenticated:
        if not user.verified:
            DAO.verify_user(user)
        resp = jsonify({'Status': AUTHENTICATED, 'FlowType': flow_type})
        app.logger.info(f'{user.username} has been authenticated.')
        return resp

    else:
        session['otp_attempts'] += 1
        app.logger.error(f'{user.username} failed authentication {session.get("otp_attempts")} time(s).')
        return jsonify({'Status': FAIL, 'Message': RETRY_MSG})


