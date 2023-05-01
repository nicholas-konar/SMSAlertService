# Status
AUTHENTICATED = 'AUTHENTICATED'
BLOCKED = 'BLOCKED'
ERROR = 'ERROR'
FAIL = 'FAIL'
SUCCESS = 'SUCCESS'

# Screen Content
BLOCKED_MSG = 'Something went wrong. Please contact support@smsalertservice.com for assistance.'
ERROR_MSG = 'There was a problem sending your code. Please contact support@smsalertservice.com for assistance.'
FAIL_MSG = 'There was a problem sending your code. Please contact support@smsalertservice.com for assistance.'

MAX_ATTEMPS_MSG = 'Max attempts limit reached. Please contact support@smsalertservice.com for assistance.'
MAX_RESENDS_MSG = 'Max resends limit reached. Please contact support@smsalertservice.com for assistance.'

CREATE_ACCOUNT_FAIL_MSG = 'We were unable to create your account. Please contact support@smsalertservice.com for assistance.'

USERNAME_TAKEN_MSG = "This username is unavailable."
INVALID_LOGIN_MSG = "Incorrect username or password."
RESEND_MSG = 'Another code is on the way.'
RETRY_MSG = "Incorrect code. Please try again."
INVALID_PH_MSG = "Please enter a valid phone number."
PW_RESET_SUCCESS = 'Your password has been reset.' # todo: fix typo (missing _MSG)

# Configs
SESSION_TIMEOUT = 1800 # 30 minutes
MAX_ATTEMPTS =3
MAX_RESENDS = 3
MAX_LOGIN_ATTEMPTS = 3