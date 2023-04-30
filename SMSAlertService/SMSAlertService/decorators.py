from functools import wraps
from flask import session, request, redirect, url_for
from SMSAlertService.dao import DAO


def admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
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
        user_id = session.get('user_id')
        user = DAO.get_user(user_id)

        if 'username' not in session or session_cookie is None:
            return redirect(url_for('site_nav_controller.login'))

        elif user.cookie != session_cookie:
            return redirect(url_for('site_nav_controller.login'))

        return func(*args, **kwargs)
    return decorated_function


