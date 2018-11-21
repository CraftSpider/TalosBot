
from typing import Type

from . import lexers, interpreters


class CommandLang:

    __slots__ = ("_lexer", "_interpreter")

    _lexer: lexers.CLLexer
    _interpreter: interpreters.CLInterpreter

    def __init__(self, lexer: lexers.CLLexer = ..., interpreter: interpreters.CLInterpreter = ...) -> None: ...

    @staticmethod
    def _operators_exist(command_str: str) -> bool: ...