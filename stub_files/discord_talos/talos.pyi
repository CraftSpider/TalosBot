"""
    Talos stub file for typing and such

    author: CraftSpider
"""
from typing import List, Tuple, Union, Any, Dict, Pattern, TypeVar, Type
import logging
import discord
import discord.ext.commands as commands
import datetime
import spidertools.common as utils
import spidertools.command_lang as cl
import spidertools.discord as dutils

C = TypeVar("C", bound=commands.Context)

TOKEN_FILE: str = ...
FILE_BASE: Dict[str, Any] = ...
_mentions_transforms: Dict[str, str] = ...
_mention_pattern: Pattern = ...
_log_event_colors: Dict[str, discord.Colour] = ...
log: logging.Logger = ...

class FakeMessage:

    __slots__ = ("guild", "channel", "author")

    guild: discord.Guild
    channel: discord.TextChannel
    author: discord.Member

    def __init__(self, guild: discord.Guild, channel: discord.TextChannel) -> None: ...

class Talos(dutils.ExtendedBot):

    VERSION: str = ...
    BOOT_TIME: datetime = ...
    PROMPT_TIME: int = ...
    DEFAULT_PREFIX: str = ...
    extension_dir: str = ...
    startup_extensions: Tuple[str, ...] = ...
    DEVS: Tuple[int, int, int] = ...
    database: utils.TalosDatabase
    session: utils.TalosHTTPClient

    # noinspection PyMissingConstructor
    def __init__(self, **kwargs: Any) -> None: ...

    def __setattr__(self, key: str, value: Any) -> None: ...

    def should_embed(self, ctx: commands.Context) -> bool: ...

    def get_timezone(self, ctx: commands.Context) -> datetime.timezone: ...

    async def logout(self) -> None: ...

    async def close(self) -> None: ...

    async def get_context(self, message: discord.Message, *, cls: Type[C] = ...) -> C: ...

    async def process_commands(self, message: discord.Message) -> None: ...

    async def mod_log(self, ctx: commands.Context, event: str, user: Union[discord.User, discord.Member], message: str) -> bool: ...

    async def on_ready(self) -> None: ...

    async def on_guild_join(self, guild: discord.Guild) -> None: ...

    async def on_guild_remove(self, guild: discord.Guild) -> None: ...

    async def on_member_ban(self, guild: discord.Guild, user: discord.User) -> None: ...

    async def on_command(self, ctx: commands.Context) -> None: ...

    async def on_command_error(self, ctx: commands.Context, exception: commands.CommandError) -> None: ...

runner: cl.CommandLang = ...

def custom_creator(name: str, text: str) -> commands.Command: ...

def talos_prefix(bot: Talos, message: discord.Message) -> Union[List[str], str]: ...

def configure_logging() -> None: ...

def load_token_file(filename: str) -> Dict[str, Union[str, List[str]]]: ...

def make_token_file(filename: str) -> None: ...

def main() -> None: ...
