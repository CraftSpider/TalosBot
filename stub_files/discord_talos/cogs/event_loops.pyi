"""
    Stub file for Talos event loops

    author: CraftSpider
"""

from typing import List, Dict, Union, Tuple, Callable, Awaitable, Optional, Any
from discord_talos.talos import Talos
import utils.command_lang as command_lang
import logging
import argparse
import googleapiclient.discovery
import oauth2client.client
import utils
import utils.dutils as dutils
import datetime as dt

SCOPES: str = ...
CLIENT_SECRET_FILE: str = ...
APPLICATION_NAME: str = ...
log: logging.Logger = ...
cl_parser: command_lang.ContextLessCL()

class SpreadsheetService(googleapiclient.discovery.Resource):

    def spreadsheets(self) -> None: ...

class EventLoops(utils.TalosCog):

    __slots__: Tuple[str, ...] = ('service', 'flags', 'last_guild_count', "__local_check")

    service: SpreadsheetService
    flags: argparse.ArgumentParser
    last_guild_count: int

    # noinspection PyMissingConstructor
    def __init__(self, bot: Talos) -> None: ...

    def setup_prompts(self) -> None: ...

    def get_credentials(self) -> oauth2client.client.Credentials: ...

    def create_service(self) -> googleapiclient.discovery.Resource: ...

    def get_spreadsheet(self, sheet_id: str, sheet_range: str) -> List[List[str]]: ...

    def set_spreadsheet(self, sheet_id: str, values: List[List[str]], sheet_range: str = ...) -> Dict[str, Union[str, int]]: ...

    @dutils.eventloop
    async def minute_task(self) -> None: ...

    @dutils.eventloop
    async def hourly_task(self) -> None: ...

    @dutils.eventloop
    async def daily_task(self) -> None: ...

    @dutils.eventloop
    async def uptime_task(self) -> None: ...

    @dutils.eventloop
    async def prompt_task(self) -> None: ...

def setup(bot: Talos) -> None: ...
