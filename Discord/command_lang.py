"""
    Talos CommandLang interpreter

    author: CraftSpider
"""
import re
import asyncio


def get_sub(obj, attribute):
    if attribute == "colour":
        return str(obj.colour)
    else:
        return getattr(obj, attribute)


op_priority = {
    "(": -1,
    ")": -1,
    "=": 0,
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
    "and": lambda x, y: int(x and y),
    "or": lambda x, y: int(x or y),
    "not": lambda x: int(not x),
    ":": get_sub
}


class CommandLangError(Exception):
    pass


def parse_lang(ctx, command_str):
    if _verify_syntax(command_str) is None:
        # print('"' + command_str + '"')
        return command_str
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
            elif (char == ")" and not in_logic and in_if) or char == "}":
                depth -= 1
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
                raise CommandLangError
            which_if = match.group(1)
            expression = match.group(2).lstrip()
            statement = match.group(3)
            if (which_if == "else" and expression != "") or (which_if != "else" and expression == ""):
                raise CommandLangError
            if which_if == "elif" or which_if == "else" and if_else is False:
                continue
            if which_if == "else" or _evaluate(ctx, expression):
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
                    raise CommandLangError("Invalid Sub-Attribute")
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


def _verify_syntax(command_str):
    return re.search(r"\[(?:if|elif|else) .+?\]\(.+?\)|{[\w :]+?}", command_str)


def _evaluate(ctx, expression):
    # split expression into pieces
    exec_list = re.split(r"(\W)", expression)
    # Un-Split things in quotes TODO: combine this with above for lower repetition
    quotes = []
    escapes = []
    escape = False
    for i in range(len(exec_list)):
        if not escape:
            if exec_list[i] == "\\":
                escapes.append(i)
                escape = True
            if exec_list[i] == "\"":
                quotes.append(i)
        else:
            escape = False
    for i in escapes:
        exec_list.pop(i)
    for i in range(0, len(quotes), 2):
        j = quotes[i + 1]
        i = quotes[i]
        exec_list[i:j + 1] = [''.join(exec_list[i:j + 1])]
    # Remove all the dangling spaces
    exec_list = list(filter(lambda x: x != "", map(lambda x: x.strip(), exec_list)))
    # Perform boolean evaluation
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


def _exec_op(ops, vals):
    try:
        val1 = vals.pop()
        op = ops.pop()
        if op != "not":
            val2 = vals.pop()
            vals.append(op_functions[op](val2, val1))
        else:
            vals.append(op_functions[op](val1))
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
        elif val == "d":
            val = "discriminator"
        elif val == "c":
            val = "colour"
        elif val.startswith("\"") and val.endswith("\""):
            val = val[1:-1]
        return val
