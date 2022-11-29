class User:

    def __init__(self, username, phone_number, enrolled, keywords):
        self._username = username
        self._phone_number = phone_number
        self._enrolled = enrolled
        self._keywords = keywords
        self._in_good_standing = False

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def phone_number(self):
        return self._phone_number

    @phone_number.setter
    def phone_number(self, value):
        self._phone_number = value

    @property
    def keywords(self):
        return self._keywords

    @keywords.setter
    def keywords(self, new_keywords):
        for new_keyword in new_keywords:
            self._keywords.append(new_keyword)

    @keywords.deleter
    def keywords(self):
        self._keywords = None

    @property
    def enrolled(self):
        return self._enrolled

    @enrolled.setter
    def enrolled(self, status):
        self._enrolled = status

    @property
    def in_good_standing(self):
        # if paid this month:
        # self._in_good_standing = True
        return None

    @in_good_standing.setter
    def in_good_standing(self, value):
        self._in_good_standing = value

    def keyword_found_in_post(self, post):
        keywords_found = []
        for keyword in self.keywords:
            if keyword.lower() in str(post.title).lower() or keyword in str(post.selftext).lower():
                keywords_found.append(keyword)
        return keywords_found

