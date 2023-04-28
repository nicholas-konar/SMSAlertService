import markupsafe

from flask import Blueprint
from flask import request, redirect, render_template, session, url_for, jsonify
from twilio.base.exceptions import TwilioRestException
from SMSAlertService import app, config
from SMSAlertService.dao import DAO
from SMSAlertService.otp_service import OtpService
from SMSAlertService.config import BLOCKED_MESSAGE, ERROR_MESSAGE, RESEND_MESSAGE, FAIL, RETRY_MESSAGE, MAX_ATTEMPTS, \
    BLOCKED, MAX_RESENDS


auth_bp = Blueprint('auth_controller', __name__)


@auth_bp.route("/account-recovery/send-otp", methods=["POST"])
def send():
    ph = markupsafe.escape(request.form.get('PhoneNumber'))
    try:
        user = DAO.get_user_by_phonenumber(ph)
        session['username'] = user.username
        session['phonenumber'] = user.phonenumber
        if session.get('otpResends') > config.MAX_RESENDS or user.blocked:
            app.logger.info(f'User {user.username} reached max OTP resends.')
            DAO.block_user(user)
            return render_template('account-recovery.html', status=config.BLOCKED, message=BLOCKED_MESSAGE)

        else:
            otp = OtpService.generate_otp()
            # status = OtpService.send_otp(otp, user.phonenumber) #todo: uncomment after testing
            app.logger.debug(f'Mock OTP Send to {user.username}: OTP = {otp}')
            status = 'accepted'
            if status == 'accepted':
                session['otp'] = otp
                session['otpResends'] = session.get('otpResends') + 1
                return render_template('account-verification.html')
            else:
                return render_template('account-recovery.html', status=config.FAIL, message=ERROR_MESSAGE)

    except TypeError:
        app.logger.error(f'Failed OTP delivery: TypeError exception for phone number {ph}.')
        return render_template('account-recovery.html', status=config.FAIL, message=ERROR_MESSAGE)

    except TwilioRestException:
        app.logger.info(f'Failed OTP delivery: TwilioRestException for phone number {ph}')
        return render_template('account-recovery.html', status=config.FAIL, message=ERROR_MESSAGE)


@auth_bp.route("/resend/<path>", methods=["POST"])
def resend(path):
    phonenumber = session['phonenumber']
    user = DAO.get_user_by_phonenumber(phonenumber)
    if user.blocked:
        app.logger.info(f'Blocked user {user.username} attempted to resend an OTP but was denied.')
        return render_template(f'{path}.html', status=config.BLOCKED, message=BLOCKED_MESSAGE)

    elif session.get('otpResends') > MAX_RESENDS:
        app.logger.info(f'Max resends limit reached. Blocking user {user.username}')
        DAO.block_user(user)
        return render_template(f'{path}.html', status=config.BLOCKED, message=BLOCKED_MESSAGE)

    else:
        app.logger.info(f'OTP resend requested by {user.username}.')
        otp = OtpService.generate_otp()
        # status = OtpService.send_otp(otp, user.phonenumber) #todo: uncomment after testing
        app.logger.debug(f'Mock OTP Resend to {user.username}: OTP = {otp}')
        status = 'accepted'
        if status == 'accepted':
            session['otp'] = otp
            session['otpResends'] += 1
            app.logger.info(f'Resent OTP to {user.username}')
            return render_template(f'{path}.html', status=config.SUCCESS, message=RESEND_MESSAGE)
        else:
            return render_template('account-recovery.html', status=config.FAIL, message=ERROR_MESSAGE)


@auth_bp.route("/authenticate/<path>", methods=["POST"])
def authenticate(path):
    if request.method == "POST":
        expected = session.get('otp')
        actual = markupsafe.escape(request.form.get('otp'))
        authenticated = OtpService.authenticate_otp(expected, actual)

        username = session.get('username')
        user = DAO.get_user_by_username(username)

        if authenticated:
            session['authenticated'] = True
            app.logger.info(f'User {user.username} has been authenticated.')
            if not user.verified:
                DAO.verify_user(user)
        elif session.get('otpAttempts') > MAX_ATTEMPTS:
            DAO.block_user(user)
            return render_template(f'{path}.html', status=BLOCKED, message=RETRY_MESSAGE)
        else:
            session['otpAttempts'] += 1
            app.logger.error(f'User {user.username} failed authentication.')
            return render_template(f'{path}.html', status=FAIL, message=RETRY_MESSAGE)

        if path == 'account-confirmation':
            return redirect(url_for('profile'))

        if path == 'account-verification':
            return redirect(url_for('reset_password'))


