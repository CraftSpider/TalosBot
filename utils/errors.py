"""
    Talos utils exception classes. All stored here so they can be easily imported

    Author: CraftSpider
"""


class NanoException(Exception):

    def __init__(self):
        super().__init__()

    def _set_message(self, *args):
        super().__init__(args)


class NotAUser(NanoException):

    def __init__(self, username):
        self._set_message(username)
        self.username = username


class NotANovel(NanoException):

    def __init__(self, title):
        self._set_message(title)
        self.title = title
