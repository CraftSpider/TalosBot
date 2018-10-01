"""
    Talos CommandLang interpreter. Defines the base command lang parser, which should be subclassed to override
    the command execution and value processing for specific platforms

    author: CraftSpider
"""

import io
import re
import abc

allowed_attributes = [
    "name", "colour", "id", "discriminator", "nick", "display_name"
]


def get_sub(obj, attribute):
    """
        Function for the : operator, getting a sub-attribute of something.
    :param obj: Primary object
    :param attribute: Attribute to get
    :return: Retrieved attribute
    """
    if attribute not in allowed_attributes:
        raise CommandLangError("Attempt to access invalid attribute")
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
    ":": get_sub
}


class CommandLangError(Exception):
    pass


class CommandLangInterpreter(metaclass=abc.ABCMeta):

    __slots__ = ("_buffer",)

    DEFAULT_PRIORITY = _op_priority
    DEFAULT_FUNCS = _op_functions

    @staticmethod
    def _operators_exist(command_str):
        """
            Checks that a string contains at least one CommandLang operator.
        :param command_str: String to check
        :return: boolean result of search
        """
        return bool(re.search(r"\[(?:if|elif|else) .+?\]\(.+?\)|{[\w :]+?}", command_str))

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
        try:
            val1 = values.pop()
            op = ops.pop()
            if op != "not":
                val2 = values.pop()
                values.append(self._get_function(op)(val2, val1))
            else:
                values.append(self._get_function(op)(val1))
        except IndexError:
            raise CommandLangError("One value supplied to two value operator")

    def _get_priority(self, operator):
        return self.DEFAULT_PRIORITY[operator]

    def _get_function(self, operator):
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
            raise CommandLangError("Invalid Boolean Expression")
        return bool(val_stack[0])

    def _lex_str(self, command_str):

        self._buffer = io.StringIO(command_str)
        escape = False
        raw = ""
        exec_stack = []

        char = None
        while char != "":
            char = self._buffer.read(1)

            if escape:
                raw += char
                escape = False

            if char == "\\":
                escape = True
            elif char == "[":
                if raw:
                    exec_stack.append(("raw", raw))
                    raw = ""
                stype, statement, text = self._lex_if()
                exec_stack.append((stype, statement, text))
            elif char == "{":
                if raw:
                    exec_stack.append(("raw", raw))
                    raw = ""
                text = self._lex_exec()
                exec_stack.append(("exec", text))
            elif char == "" and raw:
                exec_stack.append(("raw", raw))
            else:
                raw += char

        return exec_stack

    def _lex_if(self):

        end = False
        maybe_escape = False
        escape = False
        type_known = False
        maybe_text = False
        in_text = False
        depth = 0
        raw = ""
        stype = ""
        statement = ""
        text = ""

        char = None
        while char != "" and not end:
            char = self._buffer.read(1)

            if escape:
                raw += char
                escape = False

            if char == "\\" and not in_text:
                escape = True
            elif char == "\\":
                maybe_escape = True
            elif char == " " and not type_known:
                stype = raw
                if stype not in ("if", "elif", "else"):
                    raise CommandLangError("Invalid if statement type")
                type_known = True
                raw = ""
            elif char == "]" and not in_text:
                maybe_text = True
            elif char == "(" and maybe_text:
                if not type_known:
                    stype = raw
                    if stype not in ("if", "elif", "else"):
                        raise CommandLangError("Invalid if statement type")
                    type_known = True
                    raw = ""
                statement = raw
                raw = ""
                maybe_text = False
                in_text = True
            elif char == "(" and in_text:
                depth += 1
            elif char == ")" and in_text:
                if not maybe_escape:
                    text = raw
                    end = True
                else:
                    raw += ")"
                    maybe_escape = False
            else:
                if maybe_escape:
                    raw += "\\"
                    maybe_escape = False
                if maybe_text:
                    raw += "]"
                    maybe_text = False
                raw += char

        if stype != "else" and statement == "":
            raise CommandLangError("If statement missing boolean expression")
        elif stype == "else" and statement != "":
            raise CommandLangError("Else statement contains unexpected boolean expression")
        if not in_text:
            raise CommandLangError("If statement missing result")
        if char == "":
            raise CommandLangError("Unexpected end of expression")

        return stype, statement, text

    def _lex_exec(self):

        end = False
        escape = False
        raw = ""

        char = None
        while char != "" and not end:
            char = self._buffer.read(1)

            if escape:
                raw += char
                escape = False
            elif char == "\\":
                escape = True
            elif char == "}":
                end = True
            else:
                raw += char

        return raw

    def parse_lang(self, context, command_str):
        if not self._operators_exist(command_str):
            # if it's obviously not in the language, we're already done processing.
            return command_str
        # split input into list of execution items
        exec_stack = self._lex_str(command_str)
        # evaluate new list of items
        out = ""
        if_else = False
        for item in exec_stack:
            if item[0] == "if":
                exec_list = self._get_exec_list(item[1])
                if self._evaluate(context, exec_list):
                    out += self.parse_lang(context, item[2])
                    if_else = False
                else:
                    if_else = True
            elif item[0] == "elif" and if_else:
                exec_list = self._get_exec_list(item[1])
                if self._evaluate(context, exec_list):
                    out += self.parse_lang(context, item[2])
                    if_else = False
            elif item[0] == "else" and if_else:
                out += self.parse_lang(context, item[2])
                if_else = False
            else:
                if_else = False

            if item[0] == "exec":
                # Evaluate invoke block. First check if anything matches a variable, if so, return that. Otherwise run
                # the command.
                if ":" in item:
                    item = item[1].split(":")
                    try:
                        item = get_sub(self._process_val(context, item[0]), self._process_val(context, item[1]))
                    except AttributeError:
                        raise CommandLangError("Attempt to access invalid attribute")
                else:
                    item = self._process_val(context, item[1])

                result = self._execute_command(context, item)
                if not result:
                    out += str(item)
                elif isinstance(result, str):
                    out += result
            elif item[0] == "raw":
                out += item[1]
        return out

    @abc.abstractmethod
    def _process_val(self, context, val):
        return NotImplemented

    @abc.abstractmethod
    def _execute_command(self, context, val):
        return NotImplemented


class DiscordCL(CommandLangInterpreter):

    __slots__ = ()

    def _execute_command(self, ctx, item):
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
                if command.can_run(ctx):
                    ctx.bot.loop.create_task(ctx.invoke(command, *args))
                else:
                    ctx.bot.loop.create_task(ctx.send("Cannot Execute Command: Insufficient Permissions"))
            except Exception as e:
                print(e)
            return True
        return False

    def _process_val(self, ctx, val):
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
            return val


class ContextLessCL(DiscordCL):

    __slots__ = ()

    def _process_val(self, ctx, val):
        return str(val)
