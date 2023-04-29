import markupsafe

from flask import Blueprint
from flask import request, redirect, render_template, session, url_for
from twilio.base.exceptions import TwilioRestException
from SMSAlertService import app, config
from SMSAlertService.dao import DAO
from SMSAlertService.otp_service import OtpService
from SMSAlertService.config import MAX_RESENDS, BLOCKED, BLOCKED_MSG, MAX_ATTEMPTS, RESEND_MSG, ERROR_MSG, FAIL, \
    RETRY_MSG

auth_bp = Blueprint('auth_controller', __name__)


@auth_bp.route("/modal/challenge", methods=["GET"])
def challenge():
    return render_template('modal/challenge.html')


@auth_bp.route("/account-recovery/send-otp", methods=["POST"])
def send():
    ph = markupsafe.escape(request.form.get('PhoneNumber'))
    try:
        user = DAO.get_user_by_phonenumber(ph)
        app.logger.info(f'{user.username} {user.phonenumber}')
        session['username'] = user.username
        session['phonenumber'] = user.phonenumber
        if session.get('otp_resends') > MAX_RESENDS or user.blocked:
            app.logger.info(f'User {user.username} exceeded max OTP resends.')
            DAO.block_user(user)
            return render_template('account-recovery.html', status=config.BLOCKED, message=BLOCKED_MSG)

        else:
            otp = OtpService.generate_otp()
            # status = OtpService.send_otp(otp, user.phonenumber) #todo: uncomment after testing
            app.logger.debug(f'Mock OTP Send to {user.username}: OTP = {otp}')
            status = 'accepted'
            if status == 'accepted':
                session['otp'] = otp
                session['otp_resends'] = session.get('otp_resends') + 1
                return render_template('account-verification.html')
            else:
                return render_template('account-recovery.html', status=config.FAIL, message=ERROR_MSG)

    except TypeError:
        app.logger.error(f'Failed OTP delivery: TypeError exception for phone number {ph}.')
        return render_template('account-recovery.html', status=config.FAIL, message=ERROR_MSG)

    except TwilioRestException:
        app.logger.info(f'Failed OTP delivery: TwilioRestException for phone number {ph}')
        return render_template('account-recovery.html', status=config.FAIL, message=ERROR_MSG)


@auth_bp.route("/resend/<path>", methods=["POST"])
def resend(path):
    phonenumber = session.get('phonenumber')
    user = DAO.get_user_by_phonenumber(phonenumber)
    app.logger.info(f'Processing OTP resend request by {user.username}.')
    if user.blocked:
        app.logger.info(f'Denied OTP resend to user {user.username} because blocked status is {user.blocked}.')
        return render_template(f'{path}.html', status=config.BLOCKED, message=BLOCKED_MSG)

    elif session.get('otp_resends') > MAX_RESENDS:
        app.logger.info(f'Max resends limit reached. Blocking user {user.username}')
        DAO.block_user(user)
        return render_template(f'{path}.html', status=config.BLOCKED, message=BLOCKED_MSG)

    else:
        otp = OtpService.generate_otp()
        # status = OtpService.send_otp(otp, user.phonenumber) #todo: uncomment after testing
        app.logger.debug(f'Mock OTP Resend to {user.username}: OTP = {otp}')
        status = 'accepted'
        if status == 'accepted':
            session['otp'] = otp
            session['otp_resends'] += 1
            app.logger.info(f'Resent OTP to {user.username}')
            return render_template(f'{path}.html', status=config.SUCCESS, message=RESEND_MSG)
        else:
            return render_template('account-recovery.html', status=config.FAIL, message=ERROR_MSG)


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


