
from typing import Dict, Any
import aiohttp.web as web
import aiohttp
import pathlib
from utils.twitch.twitch_app import TwitchApp

Path = pathlib.Path
SETTINGS_FILE: str = ...
BACKUP_ERROR: str = ...
KNOWN_MIMES: Dict[str, str]

class TalosPrimaryHandler:

    _settings: Dict[str, Any]
    webmaster: Dict[str, str]
    base_path: Path
    session: aiohttp.ClientSession
    twitch_app: TwitchApp

    def __new__(cls, settings: Dict[str, Any] = ...) -> TalosPrimaryHandler:

    def __init__(self, settings: Dict[str, Any] = ...) -> None:

    async def site_get(self, request: web.Request) -> web.Response: ...

    async def api_get(self, request: web.Request) -> web.Response: ...

    async def do_head(self, request: web.Request) -> web.Response: ...

    async def api_post(self, request: web.Request) -> web.Response: ...

    async def auth_get(self, request: web.Request) -> web.Response: ...

    async def get_path(self, path: str) -> Path: ...

    async def get_response(self, path: Path) -> web.Response: ...

    async def error_code(self, code: int) -> web.Response: ...

    async def backup_error_code(self, old_code: int, new_code: int, error: Exception) -> web.Response: ...

    async def guess_mime(self, path: Path) -> str: ...


def main() -> int: ...
