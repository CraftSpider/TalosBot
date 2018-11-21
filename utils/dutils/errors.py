"""
    Talos error classes. Most will extend commands.CommandError

    author: CraftSpider
"""

import discord
import discord.ext.commands as commands


class NotRegistered(commands.CommandError):
    """
        Error raised when a Talos command requires a registered user, and the given user isn't.
    """

    def __init__(self, user, *args):
        """
            Initialize this error. Takes in the user that is missing an account as a required first parameter
        :param user: User that is missing an account
        :param args: Any additional messages or relevant objects
        """
        self.user = user
        message = str(user)
        super().__init__(message, *args)


class CustomCommandError(commands.CommandError):
    """
        Error raised by Talos custom commands when they encounter a problem
    """


class StopEventLoop(Exception):
    """
        Exception raise by EventLoops to forcibly stop the loop, overriding the persist parameter
    """

    def __init__(self, message=None):
        """
            Initialize the event loop stop. May take a message that will be preserved as a member and displayed in the
            log on stop
        :param message: Associated stop message
        """
        super().__init__(message)
        self.message = message
