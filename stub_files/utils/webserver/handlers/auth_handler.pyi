
from typing import Optional
import aiohttp.web as web
import utils.webserver.handlers.base_handler as bh

class AuthHandler(bh.BaseHandler):

    __slots__ = ("t_redirect",)

    t_redirect: Optional[str]

    def __init__(self, app: web.Application) -> None: ...

    async def get(self, request: web.Request) -> web.Response: ...

    async def twitch_start(self, request: web.Request) -> web.Response: ...

    async def twitch_complete(self, request: web.Request) -> web.Response: ...
