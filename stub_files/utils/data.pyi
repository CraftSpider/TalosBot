
from typing import Dict, List, Any, Tuple, Union, Iterable, Optional
import abc
import datetime as dt
import discord.ext.commands as commands

SqlRow = Tuple[Union[str, int], ...]

class Row(metaclass=abc.ABCMeta):

    __slots__ = ()

    def __init__(self, row: SqlRow, conv_bool: bool = ...) -> None: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __eq__(self, other) -> bool: ...

    def to_row(self) -> List[str, int]: ...

    @abc.abstractmethod
    def table_name(self) -> str: ...

class MultiRow(metaclass=abc.ABCMeta):

    __slots__ = ("_removed",)

    _removed: List[type(Row)]

    def __init__(self, data: Dict[str, Union[type(Row), List[type(Row)], Dict[Any, type(Row)]]]) -> None: ...

    def __iter__(self) -> Iterable[type(Row)]: ...

    @abc.abstractmethod
    def removed_items(self) -> List[type(Row)]: ...

class SqlConvertable(metaclass=abc.ABCMeta):

    __slots__ = ()

    def __eq__(self, other) -> bool: ...

    @abc.abstractmethod
    def sql_safe(self) -> Union[str, int]: ...

class TalosAdmin(Row):

    __slots__ = ("guild_id", "user_id")

    guild_id: int
    user_id: int

    def table_name(self) -> str: ...

class InvokedCommand(Row):

    __slots__ = ("id", "command_name", "times_invoked")

    id: int
    command_name: str
    times_invoked: int

    def table_name(self) -> str: ...

class UserTitle(Row):

    __slots__ = ("id", "title")

    id: int
    title: str

    def table_name(self) -> str: ...

class TalosUser(MultiRow):

    __slots__ = ("profile", "invoked", "titles", "options")

    profile: UserProfile
    invoked: List[InvokedCommand]
    titles: List[UserTitle]
    options: UserOptions

    @property
    def id(self) -> int: ...

    @property
    def title(self) -> str: ...

    def removed_items(self) -> List[type(Row)]: ...

    def get_favorite_command(self) -> InvokedCommand: ...

    def add_title(self, title: str) -> None: ...

    def check_title(self, title: str) -> bool: ...

    def set_title(self, title: str) -> bool: ...

    def clear_title(self) -> None: ...

    def remove_title(self, title: str) -> None: ...

class UserProfile(Row):

    __slots__ = ("id", "description", "commands_invoked", "title")

    id: int
    description: str
    commands_invoked: int
    title: str

    def table_name(self) -> str: ...

class UserOptions(Row):

    __slots__ = ("id", "rich_embeds", "prefix")

    id: int
    rich_embeds: bool
    prefix: str

    def __init__(self, row: SqlRow) -> None: ...

    def table_name(self) -> str: ...

class GuildOptions(Row):

    __slots__ = ("id", "rich_embeds", "fail_message", "pm_help", "any_color", "commands", "user_commands",
                 "joke_commands", "writing_prompts", "prompts_channel", "mod_log", "log_channel", "prefix", "timezone")

    id: int
    rich_embeds: bool
    fail_message: bool
    pm_help: bool
    any_color: bool
    commands: bool
    user_commands: bool
    joke_commands: bool
    writing_prompts: bool
    prompts_channel: str
    mod_log: bool
    log_channel: str
    prefix: str
    timezone: str

    def __init__(self, row: SqlRow) -> None: ...

    def table_name(self) -> str: ...

class PermissionRule(Row):

    __slots__ = ("id", "command", "perm_type", "target", "priority", "allow")

    id: int
    command: str
    perm_type: str
    target: str
    priority: int
    allow: bool

    def __init__(self, row: SqlRow) -> None: ...

    def __lt__(self, other: Any) -> bool: ...

    def __gt__(self, other: Any) -> bool: ...

    def table_name(self) -> str: ...

    def get_allowed(self, ctx: commands.Context) -> Optional[bool]: ...

class GuildCommand(Row):

    __slots__ = ("id", "name", "text")

    id: int
    name: str
    text: str

    def table_name(self) -> str: ...

class EventPeriod(SqlConvertable):

    __slots__ = ("_seconds",)

    _seconds: int

    def __init__(self, period: Union[EventPeriod, str]) -> None: ...

    def __str__(self) -> str: ...

    def __int__(self) -> int: ...

    @property
    def days(self) -> int: ...

    @property
    def hours(self) -> int: ...

    @property
    def minutes(self) -> int: ...

    @minutes.setter
    def minutes(self, value) -> None: ...

    @property
    def seconds(self) -> int: return

    @seconds.setter
    def seconds(self, value) -> None: ...

    def timedelta(self) -> dt.timedelta: ...

    def sql_safe(self) -> str: ...

class GuildEvent(Row):

    __slots__ = ("id", "name", "period", "last_active", "channel", "text")

    id: int
    name: str
    period: EventPeriod
    last_active: int
    channel: str
    text: str

    def __init__(self, data: SqlRow) -> None: ...

    def table_name(self) -> str: ...

class Quote(Row):

    __slots__ = ("guild_id", "id", "author", "quote")

    guild_id: int
    id: int
    author: str
    quote: str

    def table_name(self) -> str: ...
