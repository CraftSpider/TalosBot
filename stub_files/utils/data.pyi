
from typing import Dict, List, Any, Sequence, Union, Iterable, Optional
import abc
import datetime as dt
import discord.ext.commands as commands

SqlRow = Sequence[Union[str, int]]

class _EmptyVal:

    def __eq__(self, other: Any) -> bool: ...

class Row(metaclass=abc.ABCMeta):

    __slots__ = ()

    def __init__(self, row: SqlRow, conv_bool: bool = ...) -> None: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __eq__(self, other) -> bool: ...

    def to_row(self) -> List[Union[str, int]]: ...

    @classmethod
    def table_name(cls) -> str: ...

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


class Table(Row):

    __slots__ = ("catalog", "schema", "name", "type", "engine", "version", "row_format", "num_rows", "avg_row_len",
                 "data_len", "max_data_len", "index_len", "data_free", "auto_increment", "create_time", "update_time",
                 "check_time", "table_collation", "checksum", "create_options", "table_commentx")

class Column(Row):

    __slots__ = ("catalog", "schema", "table_name", "name", "position", "default", "nullable", "type", "char_max_len",
                 "bytes_max_len", "numeric_precision", "numeric_scale", "datetime_precision", "char_set_name",
                 "collation_name", "column_type", "column_key", "extra", "privileges", "comment", "generation_expr")

    catalog: str
    schema: str
    table_name: str
    name: str
    position: int
    default: Any
    nullable: str
    type: str
    char_max_len: Optional[int]
    bytes_max_len: Optional[int]
    numeric_precision: int
    numeric_scale: int
    datetime_precision: Optional[str]
    char_set_name: Optional[str]
    collation_name: Optional[str]
    column_type: str
    column_key: str
    extra: str
    privileges: str
    comment: str
    generation_expr: str

class TalosAdmin(Row):

    __slots__ = ("guild_id", "user_id")

    guild_id: int
    user_id: int
    TABLE_NAME: str = ...

class InvokedCommand(Row):

    __slots__ = ("id", "command_name", "times_invoked")

    id: int
    command_name: str
    times_invoked: int
    TABLE_NAME: str = ...

class UserTitle(Row):

    __slots__ = ("id", "title")

    id: int
    title: str
    TABLE_NAME: str = ...

class TalosUser(MultiRow):

    __slots__ = ("profile", "invoked", "titles", "options")

    profile: 'UserProfile'
    invoked: List[InvokedCommand]
    titles: List[UserTitle]
    options: 'UserOptions'

    @property
    def id(self) -> int: ...

    @property
    def title(self) -> str: ...

    def removed_items(self) -> List[type(Row)]: ...

    def get_favorite_command(self) -> Optional[InvokedCommand]: ...

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
    TABLE_NAME: str = ...

class UserOptions(Row):

    __slots__ = ("id", "rich_embeds", "prefix")

    id: int
    rich_embeds: bool
    prefix: str
    TABLE_NAME: str = ...

    def __init__(self, row: SqlRow) -> None: ...

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
    TABLE_NAME: str = ...

    def __init__(self, row: SqlRow) -> None: ...

class PermissionRule(Row):

    __slots__ = ("id", "command", "perm_type", "target", "priority", "allow")

    id: int
    command: str
    perm_type: str
    target: str
    priority: int
    allow: bool
    TABLE_NAME: str = ...

    def __init__(self, row: SqlRow) -> None: ...

    def __lt__(self, other: Any) -> bool: ...

    def __gt__(self, other: Any) -> bool: ...

    def get_allowed(self, ctx: commands.Context) -> Optional[bool]: ...

class GuildCommand(Row):

    __slots__ = ("id", "name", "text")

    id: int
    name: str
    text: str
    TABLE_NAME: str = ...

class EventPeriod(SqlConvertable):

    __slots__ = ("_seconds",)

    _seconds: int

    def __init__(self, period: Union['EventPeriod', str]) -> None: ...

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
    TABLE_NAME: str = ...

    def __init__(self, data: SqlRow) -> None: ...

class Quote(Row):

    __slots__ = ("guild_id", "id", "author", "quote")

    guild_id: int
    id: int
    author: str
    quote: str
    TABLE_NAME: str = ...
