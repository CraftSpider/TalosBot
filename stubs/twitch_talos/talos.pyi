"""
    Twitch Talos stub file
"""

from typing import Callable, Dict, Any
import logging
# import airc
airc = None

CLIENT_ID = ... # type: str
CLIENT_SECRET = ... # type: str
URL_BASE = ... # type: str

log = ... # type: logging.Logger

def generate_user_token(client_id: str, redirect: str = ...) -> str: ...

def generate_app_token(client_id: str, client_secret: str) -> Dict[str, Any]: ...

def revoke_token(client_id: str, token: str) -> bool: ...

# class Talos(airc.TwitchBot):
#
#     prefix = ... # type: str
#
#     def on_welcome(self, event: airc.Event): ...

def dev_only() -> callable: ...

def channel_specific(channel: str) -> Callable: ...

def main() -> int: ...
