
from typing import Dict, Any, List, Optional, Union, Type
import aiohttp.web as web
import utils.webserver.handlers as handlers
import pathlib
import ssl

_H = Union[handlers.BaseHandler, Type[handlers.BaseHandler]]

def load_settings(file: pathlib.Path) -> Dict[str, Any]: ...

def apply_settings(app: web.Application, settings: Dict[str, Any]) -> None: ...

def setup_ssl(root: pathlib.Path, settings: Dict[str, Any]) -> Optional[ssl.SSLContext]: ...

def add_handler(app: web.Application, handler: _H, path: str = ...) -> None: ...

def add_handlers(app: web.Application, handlers: List[_H], paths: List[str] = ...) -> None: ...

def setup(settings_path: pathlib.Path, handlers: List[_H] = ..., paths: List[str] = ...) -> web.Application: ...
