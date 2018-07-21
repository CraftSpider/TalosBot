"""
    CommandLang stub file.

    author: CraftSpider
"""
from typing import Dict, List, Any, TypeVar, Tuple
import discord.ext.commands as commands
import abc
import io

T = TypeVar("T")

def get_sub(obj: Any, attribute: str) -> Any: ...

_op_priority: Dict[str, int] = ...
_op_functions: Dict[str, callable] = ...

class CommandLangError(Exception): ...

class CommandLangInterpreter(metaclass=abc.ABCMeta):

    __slots__ = ("_buffer",)

    DEFAULT_PRIORITY: Dict[str, int] = ...
    DEFAULT_FUNCS: Dict[str, callable] = ...
    _buffer: io.StringIO

    @staticmethod
    def _operators_exist(command_str: str) -> bool: ...

    @staticmethod
    def _get_exec_list(expression: str) -> List[str]: ...

    def _exec_op(self, ops: List[str], values: List[str]) -> None: ...

    def _get_priority(self, operator: str) -> int: ...

    def _get_function(self, operator: str) -> callable: ...

    def _evaluate(self, context: T, exec_list: List[str]) -> bool: ...

    def _lex_str(self, command_str: str) -> List[Tuple[str, ...]]: ...

    def _lex_if(self) -> Tuple[str, str, str]: ...

    def _lex_exec(self) -> str: ...

    def parse_lang(self, context: T, command_str: str) -> str: ...

    @abc.abstractmethod
    def _process_val(self, context: T, val: str) -> Any: ...

    @abc.abstractmethod
    def _execute_command(self, context: T, val: str) -> bool: ...

class DiscordCL(CommandLangInterpreter):

    def _execute_command(self, ctx: commands.Context, item: str) -> bool: ...

    def _process_val(self, ctx: commands.Context, val: str) -> Any: ...

class ContextLessCL(DiscordCL):

    def _process_val(self, ctx: commands.Context, val: str) -> str: ...