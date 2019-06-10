
from typing import Optional
import aiohttp.web as web

class AuthHandler:

    __slots__ = ("app", "t_redirect")

    app: web.Application
    t_redirect: Optional[str]

    def __init__(self, app: web.Application) -> None: ...

    async def get(self, request: web.Request) -> web.Response: ...

    async def twitch_start(self, request: web.Request) -> web.Response: ...

    async def twitch_complete(self, request: web.Request) -> web.Response: ...
