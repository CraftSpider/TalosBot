
import re

from . import lexers, interpreters


class CommandLang:

    __slots__ = ("lexer", "interpreter")

    def __init__(self, lexer=None, interpreter=None):
        if lexer is None:
            lexer = lexers.DefaultCLLexer()
        if interpreter is None:
            interpreter = interpreters.DefaultCLInterpreter()
        self.lexer = lexer
        self.interpreter = interpreter

    @staticmethod
    def _operators_exist(command_str):
        """
            Checks that a string contains at least one CommandLang operator.
        :param command_str: String to check
        :return: boolean result of search
        """
        return bool(re.search(r"\[(?:if|elif|else) .+?\]\(.+?\)|{[\w :]+?}", command_str))

    def exec(self, context, code):
        if not self._operators_exist(command_str):
            # if it's obviously not in the language, we're already done processing.
            return command_str

        tokens = self.lexer.lex_lang(code)
        result = self.interpreter.interpret(context, tokens)
        return result
