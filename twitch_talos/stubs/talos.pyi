"""
    Twitch Talos stub file
"""

from typing import Dict, Any
import logging
import airc

CLIENT_ID = ... # type: str
CLIENT_SECRET = ... # type: str
URL_BASE = ... # type: str

log = ... # type: logging.Logger

class Talos(airc.TwitchBot):

    prefix = ... # type: str

    def on_welcome(self, event: airc.Event): ...

def dev_only() -> callable: ...

def channel_specific(channel: str) -> callable: ...

async def join(ctx: airc.Context, channel: str) -> None: ...

async def leave(ctx: airc.Context, channel: str) -> None: ...

async def wr(ctx: airc.Context) -> None: ...

async def settitle(ctx: airc.Context, title: str) -> None: ...