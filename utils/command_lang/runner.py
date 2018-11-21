
import re

from . import lexers, interpreters


class CommandLang:
    """
        Runner for CommandLang. This should generally stand on its own. Does any necessary setup and teardown for
        the running of the language
    """

    __slots__ = ("_lexer", "_interpreter")

    def __init__(self, lexer=None, interpreter=None):
        """
            Initialize a new CommandLang runner. Can provide a lexer and interpreter, or it uses the default builtins
        :param lexer: CLLexer to use in this runner
        :param interpreter: CLInterpreter to use in this runner
        """
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
        """
            Execute some CommandLang code in a given context
        :param context: Context to use in execution
        :param code: Code to execute
        :return: result of execution
        """
        if not self._operators_exist(code):
            # if it's obviously not in the language, we're already done processing.
            return code

        tokens = self._lexer.lex_lang(code)
        result = self._interpreter.interpret(context, tokens)
        return result
