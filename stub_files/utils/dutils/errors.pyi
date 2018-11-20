"""
    Talos errors stub file
"""

from typing import Union
import discord
import discord.ext.commands as commands

class NotRegistered(commands.CommandError):

    def __init__(self, message: Union[discord.Member, discord.User, str], *args) -> None: ...

class CustomCommandError(commands.CommandError):
    pass

class StopEventLoop(Exception):

    def __init__(self, message: str = ...) -> None: ...
