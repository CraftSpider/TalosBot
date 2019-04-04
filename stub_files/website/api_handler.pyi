
import aiohttp.web as web

from typing import Dict, Any

class APIHandler:

    __slots__ = ("app",)

    def __init__(self, app: web.Application): ...

    async def dispatch(self, path: str, data: Dict[str, Any]) -> None: ...
