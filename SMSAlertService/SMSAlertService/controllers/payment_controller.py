import re

import requests
from flask import Blueprint, request, render_template, make_response

from SMSAlertService import app, paypal, util
from SMSAlertService.dao import DAO

payment_bp = Blueprint('payment_controller', __name__)


@payment_bp.route("/modal/paypal", methods=["GET"])
def paypal_modal():
    SANDBOX_CLIENT_ID = 'ARQ2SvMKJy5FXgCDIX6HM2Z_ig8N1RK7xoGmOwZbS36L6TpAsDriybrjKq0zp88c-AxulF9VNt-afqqd'
    return render_template('modal/paypal.html', client_id=SANDBOX_CLIENT_ID)


@app.route('/paypal/payment/capture/completed', methods=['POST'])
def paypal_webhook():
    data = request.json
    if data['event_type'] == 'PAYMENT.CAPTURE.COMPLETED':

        # Transaction data
        resource = data['resource']
        user_id = resource['custom_id']
        order_id = resource["supplementary_data"]["related_ids"]["order_id"]
        transaction_id = resource['id']
        status = resource['status']

        # Fetch order data from PayPal API
        access_token = paypal.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"https://api.sandbox.paypal.com/v2/checkout/orders/{order_id}", headers=headers)
        order_details = response.json()

        # Kick phony request
        if 'name' in order_details and order_details['name'] == 'RESOURCE_NOT_FOUND':
            app.logger.error(f'Phony order_id in request: {order_details["name"]} for order_id {order_id}. Webhook request: {data}')
            return make_response('Forbidden', 403)

        else:
            # Customer data
            payer = order_details['payer']
            payer_id = payer['payer_id']
            first_name = payer['name']['given_name']
            last_name = payer['name']['surname']
            email = payer['email_address']

            # Order data
            order_description = order_details['purchase_units'][0]['items'][0]['name']
            units_purchased = int(re.findall(r'\d+', order_description)[0])

            # Payment data
            seller_receivable_breakdown = order_details['purchase_units'][0]['payments']['captures'][0]['seller_receivable_breakdown']
            gross = seller_receivable_breakdown['gross_amount']['value']
            paypal_fee = seller_receivable_breakdown['paypal_fee']['value']
            net = seller_receivable_breakdown['net_amount']['value']
            create_time = order_details['create_time']
            timestamp = util.timestamp()

            app.logger.debug(f'payer_id = {payer_id}')
            app.logger.debug(f'first_name = {first_name}')
            app.logger.debug(f'last_name = {last_name}')
            app.logger.debug(f'email = {email}')
            app.logger.debug(f'units_purchased = {units_purchased}')
            app.logger.debug(f'gross = {gross}')
            app.logger.debug(f'paypal_fee = {paypal_fee}')
            app.logger.debug(f'net = {net}')
            app.logger.debug(f'create_time = {create_time}')
            app.logger.debug(f'timestamp = {timestamp}')

            # make sure we haven't already fulfilled order_id
            # Save to db
            # text user their order is filled

            # Process order fulfillment
            user = DAO.get_user_by_id(user_id)



            return make_response('OK', 200)
    else:
        return make_response('Forbidden', 403)
