
from typing import List, Optional, Any, Tuple, Sequence, Union
from spidertools.common.data import Row, MultiRow
import discord.ext.commands as commands
import spidertools.common as common
import spidertools.discord as dutils
import datetime as dt


SqlRow = Sequence[Union[str, int]]


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

class GuildEvent(Row):

    __slots__ = ("id", "name", "period", "last_active", "channel", "text")

    id: int
    name: str
    period: dutils.EventPeriod
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

class TalosDatabase(common.GenericDatabase):

    # Guild option methods

    def get_guild_defaults(self) -> GuildOptions: ...

    def get_guild_options(self, guild_id: int) -> GuildOptions: ...

    def get_all_guild_options(self) -> List[GuildOptions]: ...

    # User option methods

    def get_user_defaults(self) -> UserOptions: ...

    def get_user_options(self, user_id: int) -> UserOptions: ...

    def get_all_user_options(self) -> List[UserOptions]: ...

    # User profile methods

    def register_user(self, user_id: int) -> None: ...

    def get_user(self, user_id: int) -> Optional[TalosUser]: ...

    def user_invoked_command(self, user_id: int, command: str) -> None: ...

    # Admins methods

    def get_admins(self, guild_id: int) -> List[TalosAdmin]: ...

    def get_all_admins(self) -> List[TalosAdmin]: ...

    # Perms methods

    def get_perm_rule(self, guild_id: int, command: str, perm_type: str, target: str) -> PermissionRule: ...

    def get_perm_rules(self, guild_id: int = ..., command: str = ..., perm_type: str = ..., target: str = ...) -> List[PermissionRule]: ...

    def get_all_perm_rules(self) -> List[PermissionRule]: ...

    # Custom guild commands

    def get_guild_command(self, guild_id: int, name: str) -> Optional[GuildCommand]: ...

    def get_guild_commands(self, guild_id: int) -> List[GuildCommand]: ...

    # Custom guild events

    def get_guild_event(self, guild_id: int, name: str) -> Optional[GuildEvent]: ...

    def get_guild_events(self, guild_id: int) -> List[GuildEvent]: ...

    # Quote methods

    def get_quote(self, guild_id: int, qid: int): ...

    def get_random_quote(self, guild_id: int): ...

    # Uptime methods

    def add_uptime(self, uptime: int) -> None: ...

    def get_uptime(self, start: int) -> List[Tuple[int]]: ...

    def remove_uptime(self, end: int) -> None: ...
