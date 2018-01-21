"""
    Stub file for Talos event loops

    author: CraftSpider
"""

from typing import List, Dict, Union, Tuple
from Discord.talos import Talos
import logging
import argparse
import asyncio
import googleapiclient.discovery
import oauth2client.client
import utils

SCOPES = ... # type: str
CLIENT_SECRET_FILE = ... # type: str
APPLICATION_NAME = ... # type: str
log = ... # type: logging.Logger

class EventLoops(utils.TalosCog):

    __slots__ = ... # type: Tuple[str, ...]

    service = ... # type: googleapiclient.discovery.Resource
    flags = ... # type: argparse.ArgumentParser
    last_guild_count = ... # type: int
    bg_tasks = ... # type: List[asyncio.Task]

    def __init__(self, bot: Talos) -> None: ...

    def __unload(self) -> None: ...

    def start_all_tasks(self) -> None: ...

    def start_uptime(self) -> None: ...

    def start_prompt(self) -> None: ...

    def start_regulars(self) -> None: ...

    def get_credentials(self) -> oauth2client.client.Credentials: ...

    def create_service(self) -> googleapiclient.discovery.Resource: ...

    def get_spreadsheet(self, sheet_id: str, sheet_range: str) -> List[List[str]]: ...

    def set_spreadsheet(self, sheet_id: str, values: List[List[str]], sheet_range: str = ...) -> Dict[str, Union[str, int]]: ...

    async def minute_task(self) -> None: ...

    async def hourly_task(self) -> None: ...

    async def daily_task(self) -> None: ...

    async def uptime_task(self) -> None: ...

    async def prompt_task(self) -> None: ...

def setup(bot: Talos) -> None: ...
