
import utils.command_lang as cl


class CommandLang:

    __slots__ = ("_lexer", "_interpreter")

    _lexer: cl.CLLexer
    _interpreter: cl.CLInterpreter

    def __init__(self, lexer: cl.CLLexer = ..., interpreter: cl.CLInterpreter = ...) -> None: ...

    @staticmethod
    def _operators_exist(command_str: str) -> bool: ...