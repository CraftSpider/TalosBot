
import re

from . import lexers, interpreters


class CommandLang:

    __slots__ = ("_lexer", "_interpreter")

    def __init__(self, lexer=None, interpreter=None):
        if lexer is None:
            lexer = lexers.DefaultCLLexer()
        if interpreter is None:
            interpreter = interpreters.DefaultCL()
        self._lexer = lexer
        self._interpreter = interpreter

    @staticmethod
    def _operators_exist(command_str):
        """
            Checks that a string contains at least one CommandLang operator.
        :param command_str: String to check
        :return: boolean result of search
        """
        return bool(re.search(r"\[(?:if|elif|else) .+?\]\(.+?\)|{[\w :]+?}", command_str))

    def exec(self, context, code):
        if not self._operators_exist(code):
            # if it's obviously not in the language, we're already done processing.
            return code

        tokens = self._lexer.lex_lang(code)
        result = self._interpreter.interpret(context, tokens)
        return result
