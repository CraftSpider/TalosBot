"""
    Twitch bot classes
"""

import irc.bot
import inspect
import logging

from . import client

log = logging.getLogger("twitch-irc.bot")


class SingleServerBot(irc.bot.SingleServerIRCBot):

    __slots__ = ("prefix", "all_commands")

    reactor_class = client.TwitchReactor

    def __init__(self, prefix, username, password, **params):
        self.prefix = prefix
        self.all_commands = {}
        server_list = [irc.bot.ServerSpec("irc.chat.twitch.tv", password=password)]

        super().__init__(server_list, username, username, **params)
        self.connection.add_global_handler("pubmsg", self._on_pubmsg, -20)

    def __str__(self):
        return "SingleServerBot()"

    def get_prefix(self, event):

        prefix = ret = self.prefix
        if callable(prefix):
            ret = prefix(self, event)
        if isinstance(prefix, (list, tuple)):
            ret = [_ for _ in prefix if _]

        if not ret:
            raise AssertionError("Invalid Prefix, may be empty string, list, or None.")

        return ret

    def add_command(self, command):
        if not isinstance(command, Command):
            raise TypeError("Passed command must subclass Command")

        if command.name in self.all_commands:
            raise ValueError("Command already exists")

        self.all_commands[command.name] = command
        log.debug("Added command {}".format(command.name))
        for alias in command.aliases:
            if alias in self.all_commands:
                raise ValueError("Command alias already exists")
            self.all_commands[alias] = command

    def command(self, *args, **kwargs):
        def decorator(func):
            result = command(*args, **kwargs)(func)
            self.add_command(result)
            return result
        return decorator

    def _on_join(self, conn, event):
        ch = event.target
        nick = event.source.nick
        if nick == conn.get_nickname():
            self.channels[ch] = client.TwitchChannel(conn, ch)
        self.channels[ch]._user(nick)

    def generate_context(self, conn, event):
        return Context(self, conn, event)

    def invoke_command(self, ctx):
        try:
            ctx.command.invoke(ctx)
        except Exception as e:
            print("Command failed with error", e)

    def _on_pubmsg(self, conn, event):
        self.handle_command(conn, event)

    def handle_command(self, conn, event):
        ctx = self.generate_context(conn, event)
        if ctx.command is not None:
            self.invoke_command(ctx)


def _split_args(message):
    quotes = False
    escape = False
    args = []
    cur = ""
    for char in message:
        if escape:
            cur += char
            escape = False
        elif char == "\\":
            escape = True
        elif char == "\"":
            quotes = not quotes
            args.append(cur)
            cur = ""
        elif not quotes and char == " ":
            args.append(cur)
            cur = ""
        else:
            cur += char
    if cur is not "":
        args.append(cur)
    return args


def _build_tags(event):
    return client.MessageTags(event.tags)


class Context(client.Messageable):
    __slots__ = ("message", "command", "invoker", "args", "invoked_prefix", "channel", "server", "bot", "user")

    def __init__(self, bot, conn, event):
        self.server = conn
        self.bot = bot
        self.channel = bot.channels.get(event.target)
        self.tags = _build_tags(event)

        self.message = event.arguments[0]
        prefix = bot.get_prefix(event)
        self.invoked_prefix = None
        if isinstance(prefix, (list, tuple)):
            for pref in prefix:
                if self.message.startswith(pref):
                    self.invoked_prefix = pref
        elif self.message.startswith(prefix):
            self.invoked_prefix = prefix

        if not self.invoked_prefix:
            self.command = None
            self.args = []
            return

        raw_list = _split_args(self.message)
        self.args = raw_list[1:]
        self.invoker = raw_list[0][len(self.invoked_prefix):]

        self.command = bot.all_commands.get(self.invoker)

    def __str__(self):
        out = "Context(Bot: {}, Invoked Prefix: {}, Message: {}, Command: {}, Arguments: {}, Server: {}, Channel: {})"
        return out.format(self.bot, self.invoked_prefix, self.message, self.command, self.args, self.server,
                          self.channel)

    def send(self, message):
        self.channel.send(message)


class Command:

    __slots__ = ("name", "callback", "active", "hidden", "aliases", "help", "params", "checks")

    def __init__(self, name, callback, **attrs):
        self.name = name
        if not isinstance(name, str):
            raise TypeError('Name of a command must be a string.')
        self.callback = callback
        self.checks = attrs.get("checks", [])
        self.active = attrs.get("active", True)
        self.hidden = attrs.get("hidden", False)
        self.aliases = attrs.get("aliases", [])
        self.help = attrs.get("help")
        signature = inspect.signature(callback)
        self.params = signature.parameters.copy()

    def _parse_arguments(self, ctx):
        # Quick notes: one arg per variable, except for positional only or keyword only.
        # Error if missing when required, keyword only it will fill with empty string.
        args = []
        kwargs = {}
        i = 0
        for param in self.params:
            if param == "ctx":
                continue
            fparam = self.params[param]  # type: inspect.Parameter
            if fparam.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD:
                try:
                    args.append(ctx.args[i])  # TODO: annotation cast
                    i += 1
                except IndexError:
                    if fparam.default != fparam.empty:
                        raise  # TODO: module errors
                    args.append(fparam.default)
            if fparam.kind is inspect.Parameter.VAR_POSITIONAL:
                for arg in ctx.args[i:]:
                    args.append(arg)
                break
            if fparam.kind is inspect.Parameter.KEYWORD_ONLY:
                kwargs[param] = ' '.join(ctx.args[i:])
                break
        return args, kwargs

    def invoke(self, ctx):
        if not self.can_run(ctx):
            return
        try:
            args, kwargs = self._parse_arguments(ctx)
            self.callback(ctx, *args, **kwargs)
        except Exception as e:
            log.warning(e)

    def can_run(self, ctx):
        for check in self.checks:
            if not check(ctx):
                return False
        return self.active


def command(name=None, cls=Command, **attrs):

    def decorator(func):
        if isinstance(func, Command):
            raise TypeError("Function is already a Command")

        try:
            checks = func.__command_checks__
            checks.reverse()
            del func.__command_checks__
        except AttributeError:
            checks = []

        help_doc = attrs.get('help')
        if help_doc is not None:
            help_doc = inspect.cleandoc(help_doc)
        else:
            help_doc = inspect.getdoc(func)
            if isinstance(help_doc, bytes):
                help_doc = help_doc.decode('utf-8')

        attrs['help'] = help_doc

        cname = name or func.__name__
        return cls(name=cname, callback=func, checks=checks, **attrs)

    return decorator


def check(predicate):

    def decorator(func):
        if isinstance(func, Command):
            func.checks.append(predicate)
        else:
            if not hasattr(func, "__command_checks__"):
                func.__command_checks__ = []
            func.__command_checks__.append(predicate)

        return func
    return decorator
