"""
    Stub file for Talos joke commands

    author: CraftSpider
"""

from Discord.talos import Talos
import logging
import utils
import discord.ext.commands as commands

log = ... # type: logging.Logger

class JokeCommands(utils.TalosCog):

    async def hi(self, ctx: commands.Context, *, extra: str = ...) -> None: ...

    async def favor(self, ctx: commands.Context) -> None: ...

    async def aesthetic(self, ctx: commands.Context, *, text: str) -> None: ...

def setup(bot: Talos) -> None: ...