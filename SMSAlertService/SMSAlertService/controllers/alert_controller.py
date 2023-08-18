import markupsafe
from flask import Blueprint, request
from SMSAlertService import app
from SMSAlertService.alert_engine import AlertEngine
from SMSAlertService.services.alert_service import AlertService

alert_bp = Blueprint('alert_controller', __name__)


@alert_bp.route("/alert/engine/run", methods=["POST"])
def notify():
    secret_key = markupsafe.escape(request.json['SecretKey'])
    if secret_key == app.secret_key:
        AlertEngine.run()
        return '', 204
    else:
        return 'Unauthorized', 401


@alert_bp.route("/alert/status", methods=["POST"])
def alert_status_webhook():
    sid = markupsafe.escape(request.values.get('MessageSid'))
    status = markupsafe.escape(request.values.get('MessageStatus'))
    AlertService.process_status_update(sid, status)
    return '', 204
