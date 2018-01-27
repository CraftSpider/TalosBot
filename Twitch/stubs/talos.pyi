"""
    Twitch Talos stub file
"""

from typing import Dict, Any
import logging
import irc.bot
import irc.client
import twitch_irc as twirc

CLIENT_ID = ... # type: str
CLIENT_SECRET = ... # type: str
URL_BASE = ... # type: str

log = ... # type: logging.Logger

class Talos(twirc.SingleServerBot):

    prefix = ... # type: str

    def __init__(self, nick: str, username: str, **params: Dict[str, Any]) -> None: ...

    def on_welcome(self, conn: twirc.TwitchConnection, event: irc.client.Event): ...

def test(ctx: twirc.Context): ...
def test2(ctx: twirc.Context): ...
def join(ctx: twirc.Context): ...
def leave(ctx: twirc.Context): ...
def stats(ctx: twirc.Context): ...