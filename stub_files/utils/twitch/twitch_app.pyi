
from typing import Any, List, Dict
import aiohttp

from . import types


class InsufficientPerms(Exception):

    def __init__(self, required: str, *args: Any) -> None: ...

class NotASubscriber(Exception):
    pass

class TwitchApp:

    __slots__ = ("_cid", "_secret", "_redirect", "_oauths", "session", "_users")

    _cid: str
    _secret: str
    _redirect: str
    _oauths: Dict[str, types.OAuth]
    session: aiohttp.ClientSession
    _users: Dict[str, types.User]

    def __init__(self, cid: str, secret: str, redirect: str = ...) -> None: ...

    async def open(self) -> None: ...

    def build_request_headers(self, name: str) -> Dict[str, str]: ...

    async def get_oauth(self, code: str) -> None: ...

    async def _get_user_oauth(self, oauth: types.OAuth) -> None: ...

    async def get_user(self, name: str) -> types.User: ...

    async def get_all_subs(self, name: str) -> List[types.Subscription]: ...

    async def close(self) -> None: ...
