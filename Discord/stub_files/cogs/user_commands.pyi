"""
    Stub for Talos user commands

    author: CraftSpider
"""

from typing import Match
from Discord.talos import Talos
import logging
import utils
import discord
import discord.ext.commands as commands

log = ... # type: logging.Logger

def space_replace(match: Match) -> str: ...

class UserCommands(utils.TalosCog):

    async def color(self, ctx: commands.Context, color: str) -> None: ...

    async def my_perms(self, ctx: commands.Context) -> None: ...

    async def register(self, ctx: commands.Context) -> None: ...

    async def deregister(self, ctx: commands.Context) -> None: ...

    async def profile(self, ctx: commands.Context, user: discord.User=None) -> None: ...

    user = ... # type: commands.Group

    class UserCtx(commands.Context):
        profile: utils.TalosUser

    async def _title(self, ctx: UserCtx, title: str = ...) -> None: ...

    async def _options(self, ctx: UserCtx) -> None: ...

    async def _stats(self, ctx: UserCtx) -> None: ...

    async def _description(self, ctx: UserCtx, *, text: str) -> None: ...

    async def _set(self, ctx: UserCtx, option: str, value: str) -> None: ...

    async def _remove(self, ctx: UserCtx, option: str) -> None: ...

def setup(bot: Talos) -> None: ...
