from SMSAlertService import util, mongo


class Otp:
    value = ''
    owner = ''
    destination = ''
    body = ''
    twilio = None

    def __init__(self, destination):
        user = mongo.get_user_by_phonenumber(destination)
        self.value = util.generate_otp()
        self.owner = user['Username']
        self.destination = destination
        self.body = f'Your verification code is {self.value}.\n\n' \
                    f'If you need help, please contact support@smsalertservice.com'

