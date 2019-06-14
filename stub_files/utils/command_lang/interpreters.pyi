"""
    CommandLang stub file.

    author: CraftSpider
"""
from typing import Dict, List, Any, TypeVar, Tuple
import discord.ext.commands as commands
import abc

T = TypeVar("T")

allowed_attributes: List[str] = ...

def get_sub(obj: Any, attribute: str) -> Any: ...

_op_priority: Dict[str, int] = ...
_op_functions: Dict[str, callable] = ...

class CLInterpreter(metaclass=abc.ABCMeta):

    __slots__ = ()

    @abc.abstractmethod
    def interpret(self, context: Any, tokens: List[Tuple[Any, ...]]): ...

class BaseInterpreter(CLInterpreter):

    __slots__ = ()

    DEFAULT_PRIORITY: Dict[str, int] = ...
    DEFAULT_FUNCS: Dict[str, callable] = ...

    @staticmethod
    def _get_exec_list(expression: str) -> List[str]: ...

    def _exec_op(self, ops: List[str], values: List[str]) -> None: ...

    def _get_priority(self, operator: str) -> int: ...

    def _get_function(self, operator: str) -> callable: ...

    def _evaluate(self, context: T, exec_list: List[str]) -> bool: ...

    def interpret(self, context: T, tokens: List[Tuple[Any]]) -> str: ...

    @abc.abstractmethod
    def _process_val(self, context: T, val: str) -> Any: ...

    @abc.abstractmethod
    def _execute_command(self, context: T, val: str) -> bool: ...

class DefaultCL(BaseInterpreter):

    __slots__ = ()

    def _process_val(self, context: Any, val: T) -> T: ...

    def _execute_command(self, context: Any, val: Any) -> True: ...


async def run_check(ctx: commands.Context, command: commands.Command, *args: Any) -> None: ...


class DiscordCL(BaseInterpreter):

    __slots__ = ()

    def _process_val(self, ctx: commands.Context, val: str) -> Any: ...

    def _execute_command(self, ctx: commands.Context, item: str) -> bool: ...

class ContextLessCL(DiscordCL):

    __slots__ = ()

    def _process_val(self, ctx: commands.Context, val: str) -> str: ...