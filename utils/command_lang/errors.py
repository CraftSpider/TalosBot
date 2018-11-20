

class CommandLangError(Exception):
    pass


class SyntaxError(CommandLangError):
    pass


class InvalidAttribute(CommandLangError):
    pass


class OperatorError(CommandLangError):
    pass
