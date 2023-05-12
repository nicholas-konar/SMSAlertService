import json


class User:
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.cookie = user_data['Cookie']
        self.username = user_data['Username']
        self.password = user_data['Password']
        self.phonenumber = user_data['PhoneNumber']
        self.keywords = user_data['Keywords']
        self.units_left = int(user_data['Units'])
        self.verified = user_data['Verified']
        self.blocked = user_data['Blocked']

    def get_keywords_json(self):
        return json.dumps(self.keywords)
