import os

from flask import Flask

application = Flask(__name__)

# import SMSAlertService.views
#
# SMSAlertService.secret_key = os.environ['sms_alert_service_secret_key']

if __name__ == "__main__":
    application.run(debug=True)

# FLASK_APP=SMSAlertService/application.py --> in terminal
