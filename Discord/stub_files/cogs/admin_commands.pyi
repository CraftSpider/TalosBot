"""
    Stub file for Talos admin commands

    author: CraftSpider
"""

from typing import Match, Callable, Dict
from collections import defaultdict
from Discord.talos import Talos
import logging
import utils
import discord
import discord.ext.commands as commands

secure_keys = ... # type: defaultdict
log = ... # type: logging.Logger

def key_generator(size: int = ..., chars: str = ...) -> str: ...

def space_replace(match: Match) -> str: ...

def op_check(self: AdminCommands, ctx: commands.Context) -> bool: ...

def dev_check() -> Callable: ...

class AdminCommands(utils.TalosCog):

    LEVELS = ... # type: Dict[str, int]
    __local_check = ... # type: Callable[Talos, commands.Context]

    async def nick(self, ctx: commands.Context, *, nickname: str) -> None: ...

    async def repeat(self, ctx: commands.Context, *, text: str) -> None: ...

    async def purge(self, ctx: commands.Context, number: str = ..., *key: str) -> None: ...

    async def talos_perms(self, ctx: commands.Context) -> None: ...

    ops = ... # type: commands.Group

    async def _ops_add(self, ctx: commands.Context, member: discord.Member) -> None: ...

    async def _ops_remove(self, ctx: commands.Context, member: str) -> None: ...

    async def _ops_list(self, ctx: commands.Context) -> None: ...

    async def _ops_all(self, ctx: commands.Context) -> None: ...

    perms = ... # type: commands.Group

    async def _p_create(self, ctx: commands.Context, command: str, level: str, allow: str, name: str = ..., priority: int = ...) -> None: ...

    async def _p_remove(self, ctx: commands.Context, command: str = ..., level: str = ..., name: str = ...) -> None: ...

    async def _p_list(self, ctx: commands.Context) -> None: ...

    async def _p_all(self, ctx: commands.Context) -> None: ...

    options = ... # type: commands.Group

    async def _opt_set(self, ctx: commands.Context, option: str, value: str) -> None: ...

    async def _opt_list(self, ctx: commands.Context) -> None: ...

    async def _opt_default(self, ctx: commands.Context, option: str) -> None: ...

    async def _opt_all(self, ctx: commands.Context) -> None: ...

    command = ... # type: commands.Group

def setup(bot: Talos) -> None: ...
