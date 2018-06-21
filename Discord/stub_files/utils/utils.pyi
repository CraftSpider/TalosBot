"""
    Talos utils stub file
"""

from typing import Dict, Union, List, Tuple, Any, Optional, overload

from Discord.talos import Talos
import logging
import aiohttp
import discord
import discord.ext.commands as dcommands
import datetime as dt
import utils.sql as tsql
import mysql.connector.cursor_cext as cursor_cext
import mysql.connector.abstracts as mysql_abstracts

import utils.paginators as paginators

log: logging.Logger = ...
fullwidth_transform: Dict[str, str] = ...
tz_map: Dict[str, float] = ...

class TalosFormatter(dcommands.HelpFormatter):

    _paginator: Union[dcommands.Paginator, paginators.PaginatedEmbed] = ...

    # noinspection PyMissingConstructor
    def __init__(self) -> None: ...

    @property
    async def clean_prefix(self) -> str: return ...

    async def get_command_signature(self) -> str: ...

    async def get_ending_note(self) -> str: ...

    @staticmethod
    def capital_split(text: str) -> str: ...

    def embed_shorten(self, text: str) -> str: ...

    def _subcommands_field_value(self, commands: List[dcommands.Command]) -> str: ...

    def _add_subcommands_to_page(self, max_width: int, commands: List[dcommands.Command]) -> None: ...

    async def format(self) -> Union[List[str], List[discord.Embed]]: ...

    async def embed_format(self) -> List[discord.Embed]: ...

    async def string_format(self) -> List[str]: ...



def to_snake_case(text: str) -> str: ...

def _perms_check(ctx: dcommands.Context) -> bool: ...

class TalosCog:

    __slots__ = ('bot', 'database', '__local_check')
    bot: Talos
    database: tsql.TalosDatabase

    def __init__(self, bot: Talos): ...

class PW:

    __slots__ = ('start', 'end', 'members')

    start: dt.datetime
    end: dt.datetime
    members: List[PWMember]

    def __init__(self) -> None: ...

    def get_started(self) -> bool: ...

    def get_finished(self) -> bool: ...

    def begin(self, tz: dt.timezone) -> None: ...

    def finish(self, tz: dt.timezone) -> None: ...

    def join(self, member: discord.Member, tz: dt.timezone) -> bool: ...

    def leave(self, member: discord.Member, tz: dt.timezone) -> bool: ...

class PWMember:

    __slots__ = ('user', 'start', 'end')

    user: discord.Member
    start: dt.datetime
    end: dt.datetime

    def __init__(self, user: discord.Member) -> None: ...

    def __str__(self) -> str: ...

    def __eq__(self, other: Any) -> bool: ...

    def get_len(self) -> dt.timedelta: ...

    def get_started(self) -> bool: ...

    def get_finished(self) -> bool: ...

    def begin(self, time: Union[dt.datetime, dt.time]) -> None: ...

    def finish(self, time: Union[dt.datetime, dt.time]) -> None: ...