"""
    Twitch Talos stub file
"""

from typing import Callable
import logging
# import airc
airc = None

CLIENT_ID = ... # type: str
CLIENT_SECRET = ... # type: str
URL_BASE = ... # type: str

log = ... # type: logging.Logger

# class Talos(airc.TwitchBot):
#
#     prefix = ... # type: str
#
#     def on_welcome(self, event: airc.Event): ...

def dev_only() -> callable: ...

def channel_specific(channel: str) -> Callable: ...
