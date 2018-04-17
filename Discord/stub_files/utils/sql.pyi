
from typing import Tuple, Dict, List, Union, Optional, Any, Iterable
from utils.user import TalosUser
import logging
import mysql.connector.cursor_cext as cursor_cext
import mysql.connector.abstracts as mysql_abstracts

log: logging.Logger

class EmptyCursor(mysql_abstracts.MySQLCursorAbstract):

    __slots__ = ()

    DEFAULT_ONE: None = ...
    DEFAULT_ALL: list = ...

    def __init__(self) -> None: ...

    def __iter__(self) -> iter: ...

    @property
    def description(self) -> Tuple: return ...
    @property
    def rowcount(self) -> int: return ...
    @property
    def lastrowid(self) -> type(None): return ...

    def callproc(self, procname: str, args: Tuple[Any, ...] = ...) -> None: ...

    def close(self) -> None: ...

    def execute(self, query: str, params: Iterable = ..., multi: bool = ...) -> None: ...

    def executemany(self, operation: str, seqparams: Iterable[Iterable]) -> None: ...

    def fetchone(self) -> type(DEFAULT_ONE): ...

    def fetchmany(self, size: int = ...) -> type(DEFAULT_ALL): ...

    def fetchall(self) -> type(DEFAULT_ALL): ...

talos_create_schema: str = ...
talos_create_table: str = ...
talos_add_column: str = ...
talos_remove_column: str = ...
talos_modify_column: str = ...
talos_tables: Dict[str, Dict[str, Union[List[str], str]]] = ...

class TalosDatabase:

    __slots__ = ("_sql_conn", "_cursor")

    _sql_conn: Optional[mysql_abstracts.MySQLConnectionAbstract]
    _cursor: Union[cursor_cext.CMySQLCursor, EmptyCursor]

    def __init__(self, sql_conn: Optional[mysql_abstracts.MySQLConnectionAbstract]) -> None: ...

    def verify_schema(self) -> None: ...

    def clean_guild(self, guild_id: int) -> None: ...

    def commit(self) -> None: ...

    def is_connected(self) -> bool: ...

    def raw_exec(self, statement: str) -> List: ...

    # Meta methods

    def get_column_type(self, table_name: str, column_name: str) -> str: ...

    def get_columns(self, table_name: str) -> List[Tuple[str, str]]: ...

    # Guild option methods

    def get_guild_default(self, option_name: str) -> Union[str, int]: ...

    def get_guild_defaults(self) -> List[Union[str, int]]: ...

    def get_guild_option(self, guild_id: int, option_name: str) -> Union[str, int]: ...

    def get_guild_options(self, guild_id: int) -> List[Union[str, int]]: ...

    def get_all_guild_options(self) -> List[Tuple[Union[str, int], ...]]: ...

    def set_guild_option(self, guild_id: int, option_name: str, value: Union[str, int]) -> None: ...

    def remove_guild_option(self, guild_id: int, option_name: str) -> None: ...

    # User option methods

    def get_user_default(self, option_name: str) -> Union[str, int]: ...

    def get_user_defaults(self) -> List[Union[str, int]]: ...

    def get_user_option(self, user_id: int, option_name: str) -> Union[str, int]: ...

    def get_user_options(self, user_id: int) -> List[Union[str, int]]: ...

    def get_all_user_options(self) -> List[Tuple[Union[str, int]]]: ...

    def set_user_option(self, user_id: int, option_name: str, value: Union[str, int]) -> None: ...

    def remove_user_option(self, user_id: int, option_name: str) -> None: ...

    # User profile methods

    def register_user(self, user_id: int) -> None: ...

    def deregister_user(self, user_id: int) -> None: ...

    def get_user(self, user_id: int) -> Optional[TalosUser]: ...

    def get_description(self, user_id: int) -> Optional[str]: ...

    def set_description(self, user_id: int, desc: str) -> None: ...

    def get_title(self, user_id: int) -> Optional[str]: ...

    def add_title(self, user_id: int, title: str) -> None: ...

    def check_title(self, user_id: int, title: str) -> bool: ...

    def set_title(self, user_id: int, title: str) -> bool: ...

    def user_invoked_command(self, user_id: int, command: str) -> None: ...

    def get_command_data(self, user_id: int) -> List[Tuple[str, int]]: ...

    def get_favorite_command(self, user_id: int) -> Tuple[str, int]: ...

    # Admins methods

    def get_all_admins(self) -> List[Tuple[int, int]]: ...

    def get_admins(self, guild_id: int) -> List[int]: ...

    def add_admin(self, guild_id: int, opname: str) -> None: ...

    def remove_admin(self, guild_id: int, opname: str) -> None: ...

    # Perms methods

    def get_perm_rule(self, guild_id: int, command: str, perm_type: str, target: str) -> Optional[Tuple[int, int]]: ...

    def get_perm_rules(self, guild_id: int = ..., command: str = ..., perm_type: str = ..., target: str = ...) -> List[Tuple[int, int]]: ...

    def get_all_perm_rules(self) -> List[Tuple[int, str, str, str, int, int]]: ...

    def set_perm_rule(self, guild_id: int, command: str, perm_type: str, allow: bool, priority: int = ..., target: str = ...) -> None: ...

    def remove_perm_rules(self, guild_id: int, command: Optional[str] = ..., perm_type: Optional[str] = ..., target: Optional[str] = ...) -> None: ...

    # Custom guild commands

    def set_guild_command(self, guild_id: int, name: str, text: str) -> None: ...

    def get_guild_command(self, guild_id: int, name: str) -> Optional[str]: ...

    def get_guild_commands(self, guild_id: int) -> List[Tuple[str, str]]: ...

    def remove_guild_command(self, guild_id: int, name: str) -> None: ...

    # Uptime methods

    def add_uptime(self, uptime: int) -> None: ...

    def get_uptime(self, start: int) -> List[Tuple[int]]: ...

    def remove_uptime(self, end: int) -> None: ...