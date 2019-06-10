
import aiohttp.web as web

from typing import Dict, Any

class APIHandler:

    __slots__ = ("app",)

    def __init__(self, app: web.Application): ...

    async def get(self, request: web.Request) -> web.Response: ...

    async def post(self, request: web.Request) -> web.Response: ...

    async def dispatch(self, path: str, data: Dict[str, Any]) -> web.Response: ...

    async def on_commands(self, commands: Dict[str, Any]) -> web.Response: ...
