
import aiohttp.web as web
import utils.webserver.handlers.base_handler as bh
import pathlib


class SiteHandler(bh.BaseHandler):

    __slots__ = ("webmaster", "base_path")

    webmaster: str
    base_path: pathlib.Path

    def __init__(self, app: web.Application) -> None: ...

    async def get(self, request: web.Request) -> web.Response: ...

    async def head(self, request: web.Request) -> web.Response: ...
