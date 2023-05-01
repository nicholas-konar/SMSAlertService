from functools import wraps
from flask import session, request, redirect, url_for

from SMSAlertService import app
from SMSAlertService.dao import DAO


def admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # todo: refine and test
        session_cookie = request.cookies.get('sms_alert_service_login')
        admin_user = DAO.get_user_by_username('ADMIN')

        if admin_user.cookie != session_cookie or session_cookie is None:
            return redirect(url_for('site_nav_controller.login'))
        return func(*args, **kwargs)
    return decorated_function


def protected(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        session_cookie = request.cookies.get('sms_alert_service_login')
        session_token = session.get('token')
        user_id = session.get('user_id')

        if user_id is None or session_cookie is None:
            app.logger.error('Access Denied: Missing cookie or user_id in session.')
            return redirect(url_for('site_nav_controller.login'))
        else:
            user = DAO.get_user_by_id(user_id)
            if user is None:
                app.logger.error('Access Denied: user_id found in session but not in records.')
                return redirect(url_for('site_nav_controller.login'))
            if user.cookie != session_cookie:
                app.logger.error('Access Denied: Invalid or counterfeit cookie.')
                return redirect(url_for('site_nav_controller.login'))
            if user.cookie != session_token:
                app.logger.error('Access Denied: User db cookie does not match session token.')
                return redirect(url_for('site_nav_controller.login'))
            return func(*args, **kwargs)
    return decorated_function


