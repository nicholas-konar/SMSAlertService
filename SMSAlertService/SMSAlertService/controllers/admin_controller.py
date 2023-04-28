from flask import Blueprint, request, redirect, render_template, session, url_for, jsonify
from twilio.base.exceptions import TwilioRestException
from SMSAlertService import app, mongo, alert_engine, util, config, twilio
from SMSAlertService.dao import DAO
from SMSAlertService.otp_service import OtpService
import markupsafe

admin_bp = Blueprint('admin_controller', __name__)


@admin_bp.route("/admin")
def admin():
    if session["ADMIN"]:
        username = session["username"]
        users = mongo.get_user_data()
        total_users = len(users)
        total_units_sent = util.calculate_total_units_sent(users)
        total_units_sold = util.calculate_total_units_sold(users)
        total_revenue = util.calculate_total_revenue(users)
        total_codes_redeemed = util.calculate_total_codes_redeemed(users)

        codes = mongo.get_codes()
        total_codes = util.calculate_issued_codes(codes)
        active_codes = util.calculate_total_active_codes(codes)

        app.logger.info(f'***ADMIN PAGE ACCESSED BY {username}')
        return render_template('admin.html', username=True, total_users=total_users, total_codes=total_codes,
                               active_codes=active_codes, total_revenue=total_revenue,
                               total_units_sent=total_units_sent, total_units_sold=total_units_sold,
                               total_codes_redeemed=total_codes_redeemed)
    else:
        return redirect(url_for("login"))


@admin_bp.route("/generate-codes", methods=["POST"])
def generate_codes():
    if session["ADMIN"]:
        reward = request.form.get('reward')
        quantity = request.form.get('quantity')
        distributor = request.form.get('distributor')
        prefix = request.form.get('prefix')
        mongo.create_promo_codes(reward, quantity, distributor, prefix)
        return redirect(url_for('admin'))
    else:
        return None
