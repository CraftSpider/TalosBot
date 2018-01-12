"""
    Talos CommandLang interpreter

    author: CraftSpider
"""
import re
from discord.ext.commands import CommandError

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


op_priority = {
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
op_functions = {
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


class CommandLangError(CommandError):
    pass


def _operators_exist(command_str):
    """
        Checks that a string contains at least one CommandLang operator.
    :param command_str: String to check
    :return: boolean result of search
    """
    return bool(re.search(r"\[(?:if|elif|else) .+?\]\(.+?\)|{[\w :]+?}", command_str))


def parse_lang(ctx, command_str):
    if not _operators_exist(command_str):  # if it's not obviously in the language, we're already done processing.
        return command_str
    # split input into list of execution items
    exec_stack = []
    depth = 0
    raw = ""
    escape = False
    in_logic = False
    in_if = False
    for char in command_str:
        if escape is False:
            if char == "\\" and depth == 0:
                escape = True
            elif char == "[" or char == "{":
                if depth == 0 and raw != "":
                    exec_stack.append("|" + raw)
                    raw = ""
                if char == "[":
                    in_logic = True
                    in_if = True
                depth += 1
                raw += char
            elif (char == ")" and not in_logic and in_if) or char == "}":  # first part is to make sure we're at the end
                depth -= 1                                                 # of the if block, not in the middle.
                raw += char
                if depth == 0:
                    in_if = False
                if depth == 0 and raw != "":
                    exec_stack.append(raw)
                    raw = ""
            elif char == "]" and in_logic is True:
                in_logic = False
                raw += char
            else:
                raw += char
        else:
            raw += char
            escape = False
    if raw != "":
        if depth != 0:
            raise CommandLangError
        exec_stack.append("|" + raw)
    # evaluate new list of items
    out = ""
    if_else = False
    for item in exec_stack:
        if item.startswith("["):
            # pull out if/elif/else and boolean expression
            # evaluate expression
            # if true, parse internals and set ifelse to false
            # if false, set ifelse to true and continue
            match = re.match(r"\[(if|elif|else)(.*?)\]\((.+)\)", item)
            if match is None:
                raise CommandLangError("Malformed if block")
            which_if = match.group(1)
            expression = match.group(2).lstrip()
            statement = match.group(3)
            if (which_if == "else" and expression != "") or (which_if != "else" and expression == ""):
                raise CommandLangError("Invalid if statement block")
            if which_if == "elif" or which_if == "else" and if_else is False:
                continue
            exec_list = _get_exec_list(expression)
            if which_if == "else" or _evaluate(ctx, exec_list):
                out += parse_lang(ctx, statement)
                if_else = False
            else:
                if_else = True
        elif item.startswith("{"):
            # Evaluate invoke block. First check if anything matches a variable, if so, return that. Otherwise run
            # the command.
            if ":" in item:
                item = item[1:-1].split(":")
                try:
                    item = get_sub(_process_val(ctx, item[0]), _process_val(ctx, item[1]))
                except AttributeError:
                    raise CommandLangError("Attempt to access invalid attribute")
            else:
                item = _process_val(ctx, item[1:-1])

            if isinstance(item, str) and " " in item:
                item = item.split()
                command = item[0]
                args = item[1:]
            else:
                command = item
                args = []
            command = ctx.bot.all_commands.get(command)
            if command:
                try:
                    ctx.bot.loop.create_task(ctx.invoke(command, *args))
                except Exception as e:
                    print(e)
            else:
                out += str(item)
        elif item.startswith("|"):
            out += item[1:]
    return out


def _get_exec_list(expression):
    """
        Creates an execution list from a string. Splits into pieces, then removes dangling spaces and lines.
    :param expression: Boolean Expression
    :return: list of either values or operators
    """
    exec_list = re.split(r"(\"(?:.*?[^\\](?:\\\\)*?)?\"|'(?:.*?[^\\](?:\\\\)*?)?'|\W)", expression)

    def slash_replace(match):
        if match.group(1):
            return "\\"*int(len(match.group(1)) / 2)
        else:
            return ""

    for i in range(len(exec_list)):
        if "\\" in exec_list[i]:
            exec_list[i] = re.sub(r"\\((?:\\\\)*)", slash_replace, exec_list[i])
    exec_list = list(filter(None, map(lambda x: x.strip(), exec_list)))
    return exec_list


def _evaluate(ctx, exec_list):
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
            cur = op_priority[item]
            if len(op_stack) and cur < op_priority[op_stack[-1]]:
                # if priority is lower, evaluate things until it's not
                while len(op_stack) and cur < op_priority[op_stack[-1]] and op_stack[-1] != "(":
                    _exec_op(op_stack, val_stack)
                if len(op_stack) and op_stack[-1] == "(":
                    op_stack.pop()
            if item != ")":
                op_stack.append(item)
        except KeyError:
            val_stack.append(_process_val(ctx, item))
    while len(val_stack) and len(op_stack):
        _exec_op(op_stack, val_stack)
    # If we have dangling operators or variables, something went wrong.
    if len(val_stack) != 1 or len(op_stack) != 0:
        raise CommandLangError("Invalid Boolean Expression")
    return bool(val_stack[0])


def _exec_op(ops, values):
    try:
        val1 = values.pop()
        op = ops.pop()
        if op != "not":
            val2 = values.pop()
            values.append(op_functions[op](val2, val1))
        else:
            values.append(op_functions[op](val1))
    except IndexError:
        raise CommandLangError("One value supplied to two value operator")


def _process_val(ctx, val):
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
