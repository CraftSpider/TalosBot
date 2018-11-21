

class CommandLangError(Exception):
    """
        Basic CommandLang error, all other errors should inherit from here
    """
    pass


class SyntaxError(CommandLangError):
    """
        Error in the syntax of your statement. Missing terminator, bad expression, etc
    """
    pass


class InvalidAttribute(CommandLangError):
    """
        Attempt to access an invalid or nonexistent attribute
    """
    pass


class OperatorError(CommandLangError):
    """
        Wrong number of arguments to an operator, or other problem with the execution of an operator
    """
    pass
