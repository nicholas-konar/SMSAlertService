import re
from flask import Blueprint, request, render_template, make_response
from bson import Decimal128
from SMSAlertService.services.alert_service import AlertService
from SMSAlertService import app, paypal
from SMSAlertService.dao import DAO

payment_bp = Blueprint('payment_controller', __name__)


@payment_bp.route("/modal/paypal", methods=["GET"])
def paypal_modal():
    return render_template('modal/paypal.html')


@app.route('/paypal/payment/capture/completed', methods=['POST'])
def paypal_webhook():
    webhook = request.json
    if webhook['event_type'] == 'PAYMENT.CAPTURE.COMPLETED':

        # Transaction data
        resource = webhook['resource']
        user_id = resource['custom_id']
        order_id = resource["supplementary_data"]["related_ids"]["order_id"]
        transaction_id = resource['id']

        # Fetch order data from PayPal API
        access_token = paypal.get_access_token()
        order_details = paypal.get_order_details(access_token, order_id)
        authenticated = paypal.authenticate_order(order_details)

        # Kick phony request
        if not authenticated:
            app.logger.error(f'Phony order #{order_id} found in webhook. Full webhook request: {webhook}')
            return make_response('Forbidden', 403)

        if found := DAO.get_user_by_order_id(order_id):
            app.logger.error(f'Order #{order_id} already fulfilled under user_id {found.id}. Requested by user_id {user_id}.')
            return make_response('OK', 200)

        else:
            app.logger.info(f'Authenticated order #{order_id}.')

            # Customer data
            payer = order_details['payer']
            payer_id = payer['payer_id']
            first_name = payer['name']['given_name']
            last_name = payer['name']['surname']
            email = payer['email_address']

            # Order data
            purchase_units = order_details['purchase_units'][0]
            order_description = purchase_units['items'][0]['name']
            units_purchased = int(re.findall(r'\d+', order_description)[0])

            # Payment data
            seller_receivable_breakdown = purchase_units['payments']['captures'][0]['seller_receivable_breakdown']
            gross = seller_receivable_breakdown['gross_amount']['value']
            paypal_fee = seller_receivable_breakdown['paypal_fee']['value']
            net = seller_receivable_breakdown['net_amount']['value']
            create_time = order_details['create_time']

            # Process order
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
                AlertService.send_order_confirmation(user=user, order_description=order_description)
                AlertService.send_admin(f'{user.username} purchased {order_description} for {gross}.')

            else:
                AlertService.send_admin(f'Failed to fill order #{order_id} for {user.username} in database.')
                app.logger.error(f'Alerted ADMIN to order fulfillment failure.')

            return make_response('OK', 200)
    else:
        return make_response('Forbidden', 403)
