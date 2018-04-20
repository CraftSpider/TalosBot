
from typing import Dict, List, Any, Tuple, Union
from utils.sql import TalosDatabase

class TalosUser:

    __slots__ = ("database", "id", "description", "total_commands", "cur_title", "invoked_data", "titles", "options")

    database: TalosDatabase
    id: int
    description: str
    total_commands: int
    cur_title: str
    invoked_data: List
    titles: List[str]
    options: UserOptions

    def __init__(self, database: TalosDatabase, data: Dict[str, List[Any]]) -> None: ...

    def get_favorite_command(self) -> Tuple[str, int]: ...

    def check_title(self, title: str) -> bool: ...

    def set_title(self, title: str) -> bool: ...

    def clear_title(self) -> None: ...

class UserOptions:

    __slots__ = ("database", "id", "rich_embeds", "prefix")

    id: int
    database: TalosDatabase
    rich_embeds: bool
    prefix: str

    def __init__(self, database: TalosDatabase, data: List[Union[str, int]]) -> None: ...

class GuildOptions:

    __slots__ = ("database", "id", "rich_embeds", "fail_message", "pm_help", "commands", "user_commands",
                  "joke_commands", "writing_prompts", "prompts_channel", "prefix", "timezone")

    database: TalosDatabase
    id: int
    rich_embeds: bool
    fail_message: bool
    pm_help: bool
    commands: bool
    user_commands: bool
    joke_commands: bool
    writing_prompts: bool
    prompts_channel: str
    prefix: str
    timezone: str

    def __init__(self, database: TalosDatabase, data: List[Union[str, int]]) -> None: ...

class PermissionRule:

    __slots__ = ("database", "id", "command", "perm_type", "target", "priority", "allow")

    database: TalosDatabase
    id: int
    command: str
    perm_type: str
    target: str
    priority: int
    allow: bool

    def __init__(self, database: TalosDatabase, data: List[Union[str, int]]) -> None: ...

    def __lt__(self, other: Any) -> bool: ...

    def __gt__(self, other: Any) -> bool: ...