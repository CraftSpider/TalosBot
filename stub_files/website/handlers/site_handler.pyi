
import aiohttp.web as web
from website.talos_server import TalosApplication


class SiteHandler:

    app: TalosApplication

    def __init__(self, app: TalosApplication) -> None: ...

    async def get(self, request: web.Request) -> web.Response: ...

    async def head(self, request: web.Request) -> web.Response: ...
