"""
    CommandLang stub file.

    author: CraftSpider
"""
from typing import Dict, List, Union, Any
import discord.ext.commands as commands

def get_sub(obj: Any, attribute: str) -> Any: ...

op_priority = ... # type: Dict[str, int]
op_functions = ... # type: Dict[str, callable]

class CommandLangError(Exception): ...

def parse_lang(ctx: commands.Context, command_str: str) -> str: ...

def _verify_syntax(command_str: str) -> bool: ...

def _evaluate(ctx: commands.Context, expression: str) -> bool: ...

def _exec_op(ops: List[str], vals: List[Union[str, float, int]]) -> None: ...

def _process_val(ctx: commands.Context, val: str) -> Any: ...