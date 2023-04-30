from functools import wraps
from flask import session, request, redirect, url_for

from SMSAlertService import app
from SMSAlertService.dao import DAO


def admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # todo: refine and test
        session_cookie = request.cookies.get('cookie')
        admin_user = DAO.get_user_by_username('ADMIN')

        if admin_user.cookie != session_cookie or session_cookie is None:
            return redirect(url_for('site_nav_controller.login'))
        return func(*args, **kwargs)
    return decorated_function


def protected(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        session_cookie = request.cookies.get('cookie')

        if user_id := session.get('user_id') is None or session_cookie is None:
            return redirect(url_for('site_nav_controller.login'))
        else:
            user = DAO.get_user(user_id)
            if user is None or user.cookie != session_cookie:
                return redirect(url_for('site_nav_controller.login'))
            return func(*args, **kwargs)
    return decorated_function


