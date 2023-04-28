from flask import Blueprint, request, redirect, render_template, session, url_for, jsonify
from SMSAlertService import alert_engine

alert_bp = Blueprint('alert_controller', __name__)


@alert_bp.route("/notify", methods=["GET"])
def notify():
    alert_engine.run()
    return jsonify({'status': True})

