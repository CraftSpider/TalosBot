"""
    Stub file for Talos joke commands

    author: CraftSpider
"""

from typing import Union, Dict
from discord_talos.talos import Talos
import logging
import datetime as dt
import spidertools.discord as dutils
import discord.ext.commands as commands

log: logging.Logger = ...

class JokeCommands(dutils.TalosCog):

    SUB_REPLACE: Dict[str, str]

    async def hi(self, ctx: commands.Context, *, extra: str = ...) -> None: ...

    async def favor(self, ctx: commands.Context) -> None: ...

    async def aesthetic(self, ctx: commands.Context, *, text: str) -> None: ...

    async def catpic(self, ctx: commands.Context) -> None: ...

    async def xkcd(self, ctx: commands.Context) -> None: ...

    async def smbc(self, ctx: commands.Context, comic: Union[dt.date, int, str] = ...) -> None: ...

    async def tvtropes(self, ctx: commands.Context, trope: str) -> None: ...

def setup(bot: Talos) -> None: ...