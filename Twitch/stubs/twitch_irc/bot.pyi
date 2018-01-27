"""
    twitch_irc bot stub file
"""

from typing import Tuple, Union, Callable, List, Dict, Any
import irc.bot
import irc.client
import inspect
import logging
from . import client

log = ... # type: logging.Logger

class SingleServerBot(irc.bot.SingleServerIRCBot):

    __slots__ = ... # type: Tuple[str, ...]

    reactor_class = ... # type: client.TwitchReactor

    prefix = Union[str, List[str], Callable[('SingleServerBot', irc.client.Event), Union[str, List[str]]]]
    all_commands = Dict[str, 'Command']

    def __init__(self, prefix: Union[str, List[str], Callable[[SingleServerBot, irc.client.Event], Union[str, List[str]]]],
                 username: str, password: str, **params: Dict[str, Any]) -> None: ...

    def __str__(self) -> str: ...

    def get_prefix(self, event: irc.client.Event) -> Union[str, List[str]]: ...

    def add_command(self, command: Command) -> None: ...

    def command(self, *args: Tuple[...], **kwargs:Dict[str, Any]) -> Callable[[function], Command]: ...

    def _on_join(self, conn: client.TwitchConnection, event: irc.client.Event) -> None: ...

    def generate_context(self, conn: client.TwitchConnection, event: irc.client.Event) -> Context: ...

    def invoke_command(self, ctx: Context) -> None: ...

    def on_pubmsg(self, conn: client.TwitchConnection, event: irc.client.Event) -> None: ...

    def handle_command(self, conn: client.TwitchConnection, event: irc.client.Event) -> None: ...

def _split_args(message: str) -> List[str]: ...

def _build_user(event: irc.client.Event) -> client.MessageTags: ...

class Context(client.Messageable):

    __slots__ = ... # type: Tuple[str, ...]

    bot = ... # type: SingleServerBot
    invoked_prefix = ... # type: str
    message = ... # type: str
    command = ... # type: Command
    args = ... # type: List[str]
    server = ... # type: client.TwitchConnection
    channel = ... # type: client.TwitchChannel
    tags = ... # type: client.MessageTags

    def __init__(self, bot: SingleServerBot, conn: client.TwitchConnection, event: irc.client.Event) -> None: ...

    def __str__(self) -> str: None

    def send(self, message: Any) -> None: ...

class Command:

    __slots__ = ... # type: Tuple[str, ...]

    name = ... # type: str
    callback = ... # type: Callable
    active = ... # type: bool
    hidden = ... # type: bool
    aliases = ... # type: List[str]
    help = ... # type: str
    params = ... # type: Dict[str, inspect.Parameter]
    checks = ... # type: List[Callable[[Context], bool]]

    def __init__(self, name: str, callback: Callable, **attrs: Dict[str, Any]) -> None: ...

    def _parse_arguments(self, ctx: Context) -> Tuple[List, Dict]: ...

    def invoke(self, ctx: Context) -> None: ...

    def can_run(self, ctx) -> bool: ...

def command(name: str = ..., cls: type(Command) = ..., **attrs: Dict[str, Any]) -> Callable[[function], Command]: ...

def check(predicate: Callable) -> Callable: ...
