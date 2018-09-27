"""
    Talos error classes. Most will extend commands.CommandError

    author: CraftSpider
"""

import discord
import discord.ext.commands as commands


class NotRegistered(commands.CommandError):
    """Error raised when a Talos command requires a registered user, and the given user isn't."""

    def __init__(self, message, *args):
        if type(message) == discord.Member or type(message) == discord.User:
            message = str(message)
        super().__init__(message, *args)


class CustomCommandError(commands.CommandError):
    pass
