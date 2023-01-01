import secrets
import string

from SMSAlertService import app, mongo


def generate_otp():
    length = 6
    code = ''.join(secrets.choice(string.digits)
                   for i in range(length))
    app.logger.info(f"Generated OTP '{code}'")
    return code


def authenticate(ph, otp):
    user = mongo.get_user_by_phonenumber(ph)
    if otp == user['OTP']:
        return True
    else:
        return False


def generate_code(prefix):
    length = 6
    code = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                   for i in range(length))
    code = prefix.upper() + "-" + code.upper()
    app.logger.info(f"Generated random string '{code}'")
    return code


def calculate_issued_codes(codes):
    return len(codes)


def filter_active_codes(codes):
    active_codes = []
    for code in codes:
        if code['Active']:
            active_codes.append(code)
    return active_codes


def calculate_total_active_codes(codes):
    active_codes = filter_active_codes(codes)
    return len(active_codes)


def calculate_total_revenue(users):
    total_revenue = 0
    for user in users:
        revenue = user['TotalRevenue']
        total_revenue += int(revenue)
    return total_revenue


def calculate_total_units_sent(users):
    total_msgs_sent = 0
    for user in users:
        msg_data = user['TwilioRecords']
        total_msgs_sent += len(msg_data)
    return total_msgs_sent


def calculate_total_units_sold(users):
    units_sold = 0
    for user in users:
        units = user['UnitsPurchased']
        units_sold += int(units)
    return units_sold


def calculate_total_codes_redeemed(users):
    total_codes_redeemed = 0
    for user in users:
        codes_redeemed = user['PromoCodeRecords']
        total_codes_redeemed += len(codes_redeemed)
    return total_codes_redeemed
