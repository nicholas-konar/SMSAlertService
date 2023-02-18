from SMSAlertService import util, mongo


class Otp:
    otp = ''
    owner = ''
    destination = ''
    body = ''
    twilio_data = None

    def __init__(self, destination):
        user = mongo.get_user_by_phonenumber(destination)
        self.otp = util.generate_otp()
        self.owner = user['Username']
        self.destination = destination
        self.body = f'Your verification code is {self.otp}.\n\n' \
                    f'If you need help, please contact support@smsalertservice.com'

