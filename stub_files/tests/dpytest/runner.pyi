
from typing import NamedTuple, List, BinaryIO, Union
import asyncio
import discord
import discord.ext.commands as commands

AnyChannel = Union[discord.abc.GuildChannel, discord.abc.PrivateChannel]


class RunnerConfig(NamedTuple):
    client: discord.Client
    guilds: List[discord.Guild]
    channels: List[discord.abc.GuildChannel]
    members: List[discord.Member]

_cur_config: RunnerConfig = ...
sent_queue: asyncio.Queue
error_queue: asyncio.Queue

async def run_all_events() -> None: ...

def verify_message(text: str = ..., equals: bool = ...) -> None: ...

def verify_embed(embed: discord.Embed = ..., allow_text: bool = ..., equals: bool = ...) -> None: ...

def verify_file(file: BinaryIO = ..., allow_text: bool = ..., equals: bool = ...) -> None: ...

async def empty_queue() -> None: ...

async def message_callback(message: discord.Message) -> None: ...

async def error_callback(ctx: commands.Context, error: commands.CommandError) -> None: ...

async def message(content: str, client: discord.Client = ..., channel: Union[AnyChannel, int] = ..., member: Union[discord.Member, int] = ...) -> None: ...

def get_config() -> RunnerConfig: ...

def configure(client: discord.Client, num_guilds: int = ..., num_channels: int = ..., num_members: int = ...) -> None: ...
