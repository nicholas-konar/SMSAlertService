from flask import Blueprint, jsonify
from SMSAlertService.alert_engine import AlertEngine

alert_bp = Blueprint('alert_controller', __name__)


@alert_bp.route("/notify", methods=["GET"])
def notify():
    AlertEngine.run()
    return jsonify({'status': True})

