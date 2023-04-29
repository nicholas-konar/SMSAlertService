import markupsafe

from flask import Blueprint
from flask import request, redirect, render_template, session, url_for, jsonify
from twilio.base.exceptions import TwilioRestException
from SMSAlertService import app, config
from SMSAlertService.dao import DAO
from SMSAlertService.otp_service import OtpService
from SMSAlertService.config import MAX_RESENDS, BLOCKED, BLOCKED_MSG, MAX_ATTEMPTS, RESEND_MSG, ERROR_MSG, FAIL, \
    RETRY_MSG, SUCCESS, FAIL_MSG, ERROR

auth_bp = Blueprint('auth_controller', __name__)


@auth_bp.route("/modal/authenticate", methods=["GET"])
def challenge():
    session['otp_resends'] = 0
    session['otp_attempts'] = 0
    return render_template('modal/authenticate.html')


@auth_bp.route("/send/otp", methods=["POST"])
def send():
    ph = markupsafe.escape(request.json['PhoneNumber'])
    user = DAO.get_user_by_phonenumber(ph)

    if user is None:
        return jsonify({'Status': FAIL, 'Message': FAIL_MSG})

    elif session.get('otp_resends') >= MAX_RESENDS or user.blocked:
        app.logger.info(f'User {user.username} exceeded max OTP resends.')
        DAO.block_user(user)
        return jsonify({'Status': BLOCKED, 'Message': BLOCKED_MSG})

    else:
        try:
            otp = OtpService.generate_otp()
            # status = OtpService.send_otp(otp, user.phonenumber) #todo: uncomment after testing
            app.logger.debug(f'Mock OTP Send to {user.username}: OTP = {otp}')
            session['username'] = user.username
            session['phonenumber'] = user.phonenumber
            session['otp_resends'] += 1
            app.logger.debug(f'Resend count = {session["otp_resends"]}')
            session['otp'] = otp
            return jsonify({'Status': SUCCESS, 'OTP': otp})

        except TwilioRestException:
            app.logger.info(f'OTP delivery error: TwilioRestException for phone number {ph}')
            return jsonify({'Success': ERROR, 'Message': ERROR_MSG})


@auth_bp.route("/resend/<path>", methods=["POST"])
def resend(path):
    phonenumber = session.get('phonenumber')
    user = DAO.get_user_by_phonenumber(phonenumber)
    app.logger.info(f'Processing OTP resend request by {user.username}.')
    if user.blocked:
        app.logger.info(f'Denied OTP resend to user {user.username}: Blocked status is {user.blocked}.')
        return render_template(f'{path}.html', status=config.BLOCKED, message=BLOCKED_MSG)

    elif session.get('otp_resends') > MAX_RESENDS:
        app.logger.info(f'Max resends limit reached. Blocking user {user.username}')
        DAO.block_user(user)
        return render_template(f'{path}.html', status=config.BLOCKED, message=BLOCKED_MSG)

    else:
        otp = OtpService.generate_otp()
        # message = OtpService.send_otp(otp, user.phonenumber) #todo: uncomment after testing
        app.logger.debug(f'Mock OTP Resend to {user.username}: OTP = {otp}')
        session['otp'] = otp
        session['otp_resends'] += 1 # todo: test this
        app.logger.info(f'Resent OTP to {user.username}')
        return render_template(f'{path}.html', status=config.SUCCESS, message=RESEND_MSG)


@auth_bp.route("/authenticate/otp", methods=["POST"])
def authenticate(path):
    expected = session.get('otp')
    actual = markupsafe.escape(request.form.get('otp'))
    authenticated = OtpService.authenticate_otp(expected, actual)

    username = session.get('username')
    user = DAO.get_user_by_username(username)

    if session.get('otp_attempts') > MAX_ATTEMPTS:
        DAO.block_user(user)
        return render_template(f'{path}.html', status=BLOCKED, message=BLOCKED_MSG)

    if authenticated:
        session['authenticated'] = True
        app.logger.info(f'User {user.username} has been authenticated.')
        if not user.verified:
            DAO.verify_user(user)
    else:
        session['otp_attempts'] += 1
        app.logger.error(f'User {user.username} failed authentication {session.get("otp_attempts")} time(s).')
        return render_template(f'{path}.html', status=FAIL, message=RETRY_MSG)

    if path == 'account-confirmation':
        return redirect(url_for('profile'))

    if path == 'account-verification':
        return redirect(url_for('reset_password'))


