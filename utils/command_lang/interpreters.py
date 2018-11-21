"""
    Talos CommandLang interpreter. Defines the base command lang parser, which should be subclassed to override
    the command execution and value processing for specific platforms

    author: CraftSpider
"""

import re
import abc

from . import errors
from .enums import Instruction

_allowed_attributes = [
    "name", "colour", "id", "discriminator", "nick", "display_name"
]


def _get_sub(obj, attribute):
    """
        Function for the : operator, getting a sub-attribute of something.
    :param obj: Primary object
    :param attribute: Attribute to get
    :return: Retrieved attribute
    """
    if attribute not in _allowed_attributes:
        raise errors.InvalidAttribute(f"Attempt to access invalid attribute {attribute}")
    if attribute == "colour":
        return str(obj.colour)
    return getattr(obj, attribute)


_op_priority = {
    "(": -1,
    ")": -1,
    "=": 0,
    "is": 0,
    "or": 10,
    "+": 10,
    "-": 10,
    "and": 20,
    "*": 20,
    "/": 20,
    "^": 30,
    "not": 30,
    ":": 40,
}
_op_functions = {
    "=": lambda x, y: int(x == y),
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "*": lambda x, y: x * y,
    "/": lambda x, y: x / y,
    "^": lambda x, y: x**y,
    "is": lambda x, y: int(x is y),
    "and": lambda x, y: int(x and y),
    "or": lambda x, y: int(x or y),
    "not": lambda x: int(not x),
    ":": _get_sub
}


class CLInterpreter(metaclass=abc.ABCMeta):
    """
        Abstract base for CommandLang interpreters. Defines the interface they are expected to provide
    """

    __slots__ = ()

    @abc.abstractmethod
    def interpret(self, context, tokens):
        """
            Run the CL Interpreter. Should return the result of interpreting the provided
            list of tokens
        :param context: Context to evalute tokens in
        :param tokens: List of CL tokens provided by lexer
        :return: Result of evaluation
        """


class BaseInterpreter(CLInterpreter):
    """
        Base CommandLangInterpreter Class. This is an abstract class for all concrete CommandLang interpreters, that
        provides the primary parsing mechanism and delegates to subclasses for resolution of variables.

        CommandLang is a simple markdown styled language, allowing imperative statements and simple conditionals. The
        language is not Turing Complete, as there is no facility for looping or advanced control flow.
    """

    __slots__ = ()

    DEFAULT_PRIORITY = _op_priority
    DEFAULT_FUNCS = _op_functions

    @staticmethod
    def _get_exec_list(expression):
        """
            Creates an execution list from a string. Splits into pieces, then removes dangling spaces and lines.
        :param expression: Boolean Expression
        :return: list of either values or operators
        """
        exec_list = re.split(r"(\"(?:.*?[^\\](?:\\\\)*?)?\"|'(?:.*?[^\\](?:\\\\)*?)?'|\W)", expression)

        def slash_replace(match):
            if match.group(1):
                return "\\" * int(len(match.group(1)) / 2)
            else:
                return ""

        for i in range(len(exec_list)):
            if "\\" in exec_list[i]:
                exec_list[i] = re.sub(r"\\((?:\\\\)*)", slash_replace, exec_list[i])
        exec_list = list(filter(None, map(lambda x: x.strip(), exec_list)))
        return exec_list

    def _exec_op(self, ops, values):
        """
            Execute a boolean operator, alter the values list appropriately
        :param ops: Operator list
        :param values: Values list
        """
        try:
            val1 = values.pop()
            op = ops.pop()
            if op != "not":
                val2 = values.pop()
                values.append(self._get_function(op)(val2, val1))
            else:
                values.append(self._get_function(op)(val1))
        except IndexError:
            raise errors.OperatorError("One value supplied to two value operator")

    def _get_priority(self, operator):
        """
            Get the priority of a given operator
        :param operator: Operator to get priority of
        :return: Priority of the operator, an int between MIN_INT and MAX_INT
        """
        return self.DEFAULT_PRIORITY[operator]

    def _get_function(self, operator):
        """
            Get the function for a given operator
        :param operator: Operator to get function of
        :return: Internal function of operator, which will be called with supplied values
        """
        return self.DEFAULT_FUNCS.get(operator, lambda: None)

    def _evaluate(self, ctx, exec_list):
        """
            Performs boolean evaluation on a list of values and operators
        :param ctx: commands.Context object
        :param exec_list: List to evaluate
        :return: boolean result of the list evaluation
        """
        op_stack = []
        val_stack = []
        for item in exec_list:
            try:
                if item == "(":
                    op_stack.append(item)
                    continue
                cur = self._get_priority(item)
                if len(op_stack) and cur < self._get_priority(op_stack[-1]):
                    # if priority is lower, evaluate things until it's not
                    while len(op_stack) and cur < self._get_priority(op_stack[-1]) and op_stack[-1] != "(":
                        self._exec_op(op_stack, val_stack)
                    if len(op_stack) and op_stack[-1] == "(":
                        op_stack.pop()
                if item != ")":
                    op_stack.append(item)
            except KeyError:
                val_stack.append(self._process_val(ctx, item))
        while len(val_stack) and len(op_stack):
            self._exec_op(op_stack, val_stack)
        # If we have dangling operators or variables, something went wrong.
        if len(val_stack) != 1 or len(op_stack) != 0:
            raise errors.SyntaxError("Invalid Boolean Expression")
        return bool(val_stack[0])

    def interpret(self, context, tokens):
        """
            Parse and execute a CommandLang statement
        :param context: Context object to use for the parsing of variables
        :param tokens: List of lexed tokens to interpret
        :return: Result of interpreting
        """
        out = ""
        if_else = False
        for item in tokens:
            if item[0] == Instruction.IF:
                exec_list = self._get_exec_list(item[1])
                if self._evaluate(context, exec_list):
                    out += self.interpret(context, item[2])
                    if_else = False
                else:
                    if_else = True
            elif item[0] == Instruction.ELIF and if_else:
                exec_list = self._get_exec_list(item[1])
                if self._evaluate(context, exec_list):
                    out += self.interpret(context, item[2])
                    if_else = False
            elif item[0] == Instruction.ELSE and if_else:
                out += self.interpret(context, item[2])
                if_else = False
            else:
                if_else = False

            if item[0] == Instruction.EXEC:
                # Evaluate invoke block. First check if anything matches a variable, if so, return that. Otherwise run
                # the command.
                val = item[1]
                if ":" in val:
                    val = val.split(":")
                    obj = self._process_val(context, val[0])
                    attr = self._process_val(context, val[1])
                    try:
                        val = self._get_function(":")(obj, attr)
                    except AttributeError:
                        raise errors.InvalidAttribute(f"Attempt to access invalid attribute {attr}")
                else:
                    val = self._process_val(context, val)

                result = False
                if val is None:
                    result = self._execute_command(context, item[1])
                if not result:
                    out += str(val)
            elif item[0] == Instruction.RAW:
                out += item[1]
        return out

    @abc.abstractmethod
    def _process_val(self, context, val):
        """
            Process a statement value for a given context
        :param context: Context to use
        :param val: Value to process
        :return: Processed value
        """
        return NotImplemented

    @abc.abstractmethod
    def _execute_command(self, context, val):
        """
            Execute a command in a given context
        :param context: Context to execute in
        :param val: Command to execute
        :return: Whether command execution succeeded
        """
        return NotImplemented


class DefaultCL(BaseInterpreter):
    """
        Default CL Interpreter. Cannot run commands, any execs return their internal values literally
    """

    __slots__ = ()

    def _process_val(self, context, val):
        """
            No value processing. Do nothing and return val unchanged
        :param context: Unused
        :param val: Value to process
        :return: val unchanged
        """
        return val

    def _execute_command(self, context, val):
        """
            Attempt to execute a command. Do nothing and return successful
        :param context: Unused
        :param val: Unused
        :return: True, indiciating successful execution
        """
        return True


async def run_check(ctx, command, *args):
    """
        Run a command with checks. If checks fail, sends a failure message to context
    :param ctx: d.py context to use
    :param command: Command object to execute with checks
    :param args: arguments to be passed to the command
    """
    if await command.can_run(ctx):
        await ctx.invoke(command, *args)
    else:
        await ctx.send("Cannot Execute Command: Insufficient Permissions")


class DiscordCL(BaseInterpreter):
    """
        CommandLang parser for discord that uses d.py contexts. Allows variable access to most attributes of the
        context related to the user posting
    """

    __slots__ = ()

    def _process_val(self, ctx, val):
        """
            Process a variable into
        :param ctx:
        :param val:
        :return:
        """
        try:
            return float(val)
        except ValueError:
            if val == "a" or val == "author":
                val = ctx.author
            elif val == "r" or val == "role":
                val = ctx.author.top_role
            elif val == "ch" or val == "channel":
                val = ctx.channel
            elif val == "cat" or val == "category":
                val = ctx.channel.category
            elif val == "n":
                val = "name"
            elif val == "disc":
                val = "discriminator"
            elif val == "c":
                val = "colour"
            elif val == "d" or val == "display":
                val = "display_name"
            elif (val.startswith("\"") and val.endswith("\"")) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            else:
                val = None
            return val

    def _execute_command(self, ctx, item):
        """
            Execute a command with the Discord ctx. Tries to find commands from the bot and add them to the asyncio
            loop of tasks to run
        :param ctx: d.py context object
        :param item: command to run
        :return: Whether command executed successfully
        """
        args = []
        if isinstance(item, str) and " " in item:
            item = item.split()
            command = item[0]
            args = item[1:]
        else:
            command = item
        command = ctx.bot.all_commands.get(command)
        if command:
            try:
                ctx.bot.loop.create_task(run_check(ctx, command, *args))
            except Exception as e:
                print(e)
            return True
        return False


class ContextLessCL(DiscordCL):
    """
        CommandLang interpreter that ignores all context
    """

    __slots__ = ()

    def _process_val(self, ctx, val):
        """
            Does no processing aside from assuring value is converted to a string and returned
        :param ctx: Unused context
        :param val: Value to process
        :return: string conversion of value
        """
        return str(val)
