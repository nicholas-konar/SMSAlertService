from flask import Blueprint, request, redirect, render_template, session, url_for, jsonify
from SMSAlertService import app, mongo

payment_bp = Blueprint('payment_controller', __name__)


@payment_bp.route("/process-sale") # todo: this data needs to come from the body of a POST request
def process_sale():
    username = session.get('username')
    status = request.args.get('status')
    units = request.args.get('units')
    amount = request.args.get('amount')
    app.logger.info(f'Processing sale of {units} units to user {username} for ${amount} - status: {status}')
    if status == "COMPLETED":
        mongo.process_transaction(username, units, amount)
        return redirect(url_for("profile"))
    else:
        return jsonify({"status": False})


