import re
import os
import requests
from flask import Blueprint, request, render_template, make_response
from bson import Decimal128

from SMSAlertService import app, paypal, util
from SMSAlertService.dao import DAO

payment_bp = Blueprint('payment_controller', __name__)


@payment_bp.route("/modal/paypal", methods=["GET"])
def paypal_modal():
    SANDBOX_CLIENT_ID = os.environ['PAYPAL_SANDBOX_CLIENT_ID']
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
        app.logger.debug(f'order_id = {order_id}')
        app.logger.debug(f'transaction_id = {transaction_id}')

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
            app.logger.error(
                f'Phony order_id in request: {order_details["name"]} for order_id {order_id}. Webhook request: {data}')
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
            seller_receivable_breakdown = order_details['purchase_units'][0]['payments']['captures'][0][
                'seller_receivable_breakdown']
            gross = seller_receivable_breakdown['gross_amount']['value']
            paypal_fee = seller_receivable_breakdown['paypal_fee']['value']
            net = seller_receivable_breakdown['net_amount']['value']
            create_time = order_details['create_time']

            # make sure we haven't already fulfilled order_id
            # Save to db
            # text user their order is filled

            # Process order fulfillment
            user = DAO.get_user_by_id(user_id)

            success = DAO.fulfill_order(user=user,
                                        payer_id=payer_id,
                                        order_id=order_id,
                                        transaction_id=transaction_id,
                                        units_purchased=int(units_purchased),
                                        gross=Decimal128(gross),
                                        paypal_fee=Decimal128(paypal_fee),
                                        net=Decimal128(net),
                                        first_name=first_name,
                                        last_name=last_name,
                                        email=email,
                                        create_time=create_time)
            if success:
                # text user
                app.logger.debug(f'Your account has been loaded with {units_purchased} alerts.')
                pass
            else:
                # text admin
                app.logger.debug(f'Oh no bro.')
                pass

            return make_response('OK', 200)
    else:
        return make_response('Forbidden', 403)
