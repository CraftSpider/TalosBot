"""
    Twitch API Wrapper.

    A wrapper for the twitch IRC API, using the irc package.
    Inspired by the discord.py module.
"""

__title__ = "twitch_irc"
__author__ = "CraftSpider"
__license__ = "MIT"
__copyright__ = "Copyright 2017-2018 CraftSpider"
__version__ = "0.1.0"

from .client import TwitchChannel, TwitchConnection
from .bot import SingleServerBot, Context, command, check
