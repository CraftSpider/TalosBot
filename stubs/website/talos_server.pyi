
from typing import Dict, Any
import aiohttp.web as web
import spidertools.webserver as webserver
import pathlib

SETTINGS_FILE: pathlib.Path = ...

class TalosAPI(webserver.APIHandler):

    __api_auth__: bool = ...

    async def on_commands(self, method: str, commands: Dict[str, Any]) -> web.Response: ...

def main() -> int: ...
