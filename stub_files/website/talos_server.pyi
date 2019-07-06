
from typing import Dict, Any
import aiohttp.web as web
import utils.webserver as webserver
import pathlib

SETTINGS_FILE: pathlib.Path = ...

class TalosAPI(webserver.APIHandler):

    async def on_commands(self, method: str, commands: Dict[str, Any]) -> web.Response: ...

def main() -> int: ...
