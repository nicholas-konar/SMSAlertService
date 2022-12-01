from flask import Flask

app = Flask(__name__)

import SMSAlertService.views

SMSAlertService.secret_key = "testing"

if __name__ == "__init__":
    SMSAlertService.app.run()

# FLASK_APP=SMSAlertService/__init__.py --> in terminal
