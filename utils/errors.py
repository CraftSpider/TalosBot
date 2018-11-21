"""
    Talos utils exception classes. All stored here so they can be easily imported

    Author: CraftSpider
"""


class NanoException(Exception):
    """
        Base exception for NaNo objects
    """

    def __init__(self):
        """
            Initialize exception, takes no arguments
        """
        super().__init__()

    def _set_message(self, *args):
        """
            Internal method used to set the exception message after creation
        :param args: Arguments to set for message
        """
        super().__init__(args)


class NotAUser(NanoException):
    """
        If the requested NaNo User does not exist or is innacessible
    """

    def __init__(self, username):
        """
            Initialize exception. Takes the username that couldn't be found as an input
        :param username: Username of the User that couldn't be found
        """
        self._set_message(username)
        self.username = username


class NotANovel(NanoException):
    """
        If the requested NaNo Novel does not exist or is innacessible
    """

    def __init__(self, title):
        """
            Initialize exception. Takes the title of the novel that couldn't be found as an input
        :param title: Title of the Novel that couldn't be found
        """
        self._set_message(title)
        self.title = title
