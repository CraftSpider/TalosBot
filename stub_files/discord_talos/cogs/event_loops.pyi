"""
    Stub file for Talos event loops

    author: CraftSpider
"""

from typing import List, Dict, Union, Tuple, Callable, Awaitable, Optional, Any
from discord_talos.talos import Talos
import utils.command_lang as command_lang
import logging
import argparse
import asyncio
import googleapiclient.discovery
import oauth2client.client
import utils
import datetime as dt

SCOPES: str = ...
CLIENT_SECRET_FILE: str = ...
APPLICATION_NAME: str = ...
log: logging.Logger = ...
cl_parser: command_lang.ContextLessCL()

def align_period(period: utils.EventPeriod) -> dt.timedelta: ...

class SpreadsheetService(googleapiclient.discovery.Resource):

    def spreadsheets(self) -> None: ...

class EventLoop:

    __slots__ = ("_task", "_callback", "period", "persist", "start_time", "loop")

    _task: asyncio.Task
    _callback: Callable[[Any], Awaitable]
    period: utils.EventPeriod
    persist: bool
    start_time: Optional[dt.datetime]
    loop: asyncio.AbstractEventLoop

    @property
    def callback(self) -> Callable[[Any], Awaitable]: ...

    @callback.setter
    def callback(self, value: Callable[[Any], Awaitable]) -> None: ...

    def set_start_time(self, time: dt.datetime) -> None: ...

    def start(self, *args: Tuple[Any, ...], **kwargs: Dict[Any, Any]) -> None: ...

    async def run(self, *args: Tuple[Any, ...], **kwargs: Dict[Any, Any]) -> None: ...

    def stop(self) -> None: ...

def eventloop(period: Union[str, utils.EventPeriod], *, persist: bool = ..., start_time: dt.datetime = ...) -> Callable[[Callable[[Any], Awaitable]], EventLoop]: ...

class EventLoops(utils.TalosCog):

    __slots__: Tuple[str, ...] = ('service', 'flags', 'last_guild_count', 'bg_tasks', "__local_check")

    service: SpreadsheetService
    flags: argparse.ArgumentParser
    last_guild_count: int
    bg_tasks: Dict[str, EventLoop]

    # noinspection PyMissingConstructor
    def __init__(self, bot: Talos) -> None: ...

    def __unload(self) -> None: ...

    def add_loop(self, period: Union[str, utils.EventPeriod], coro: Callable[[Any], Awaitable], *, persist: bool = ..., start_time: dt.datetime = ..., args: Optional[List] = ..., kwargs: Optional[Dict] = ...) -> None: ...

    def start_all_tasks(self) -> None: ...

    def start_prompt(self) -> None: ...

    def get_credentials(self) -> oauth2client.client.Credentials: ...

    def create_service(self) -> googleapiclient.discovery.Resource: ...

    def get_spreadsheet(self, sheet_id: str, sheet_range: str) -> List[List[str]]: ...

    def set_spreadsheet(self, sheet_id: str, values: List[List[str]], sheet_range: str = ...) -> Dict[str, Union[str, int]]: ...

    @eventloop
    async def minute_task(self) -> None: ...

    @eventloop
    async def hourly_task(self) -> None: ...

    @eventloop
    async def daily_task(self) -> None: ...

    @eventloop
    async def uptime_task(self) -> None: ...

    @eventloop
    async def prompt_task(self) -> None: ...

def setup(bot: Talos) -> None: ...
