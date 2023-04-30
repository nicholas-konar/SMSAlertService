from functools import wraps
from flask import session, request, redirect, url_for

from SMSAlertService import app
from SMSAlertService.dao import DAO


def protected(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        username = session.get('username')
        user = DAO.get_user_by_username(username)
        session_cookie = request.cookies.get('cookie')
        app.logger.debug(f'req cookie = {session_cookie}')
        app.logger.debug(f'user cookie = {user.cookie}')
        if 'username' not in session or session_cookie is None:
            app.logger.debug('case 1')
            return redirect(url_for('site_nav_controller.login'))
        elif user.cookie != session_cookie:
            app.logger.debug('case 2')
            return redirect(url_for('site_nav_controller.login'))
        return func(*args, **kwargs)
    return decorated_function
