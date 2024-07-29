from flask import Flask

app = Flask(__name__)

import os
from SMSAlertService.resources.config import SESSION_TIMEOUT
from SMSAlertService.controllers.account_controller import account_bp
from SMSAlertService.controllers.admin_controller import admin_bp
from SMSAlertService.controllers.alert_controller import alert_bp
from SMSAlertService.controllers.auth_controller import auth_bp
from SMSAlertService.controllers.payment_controller import payment_bp
from SMSAlertService.controllers.site_nav_controller import site_nav_bp

app.register_blueprint(account_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(alert_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(site_nav_bp)

app.secret_key = os.environ['SMS_ALERT_SERVICE_SECRET_KEY']

app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_TIME_OUT'] = SESSION_TIMEOUT


if __name__ == "__main__":
    app.run()
