
import logging
import asyncio
import discord
import discord.ext.commands as commands


class DiscordHandler(logging.Handler):

    channel: discord.abc.Messageable
    loop: asyncio.AbstractEventLoop
    queue: asyncio.Queue
    running: bool

    def __init__(self, ctx: commands.Context, level: int = ..., *, loop: asyncio.AbstractEventLoop = ...) -> None: pass

    async def _run_loop(self) -> None: ...

    def emit(self, record: logging.LogRecord) -> None: ...

    def stop(self) -> None: ...
