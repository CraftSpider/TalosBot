"""
    Twitch bot classes
"""

import irc.bot
import inspect
import logging

from . import client

log = logging.getLogger("twitch-irc.bot")

def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]


class SingleServerBot(irc.bot.SingleServerIRCBot):

    __slots__ = ["prefix", "commands"]

    reactor_class = client.TwitchReactor

    def __init__(self, prefix, server_list, nickname, realname):
        self.prefix = prefix
        self.all_commands = {}

        super().__init__(server_list, nickname, realname)

    def __str__(self):
        return "SingleServerBot()"

    def _on_join(self, conn, event):
        ch = event.target
        nick = event.source.nick
        if nick == conn.get_nickname():
            self.channels[ch] = client.TwitchChannel(conn, ch)
        self.channels[ch].add_user(nick)

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

    def generate_context(self, conn, event):
        return Context(self, conn, event)

    def on_pubmsg(self, conn, event):
        self.handle_command(conn, event)

    def handle_command(self, conn, event):
        ctx = self.generate_context(conn, event)
        # ctx.server.send_raw(" ".join(ctx.arguments))
        if ctx.command in self.all_commands:
            self.all_commands[ctx.command].invoke(ctx)


class Context(client.Messageable):
    __slots__ = ["message", "command", "arguments", "prefix", "channel", "server", "bot"]

    def __init__(self, bot, conn, event):
        self.server = conn
        self.bot = bot
        self.prefix = bot.prefix
        self.message = event.arguments[0]
        self.command = ""
        if self.message.startswith(self.prefix):
            self.command = remove_prefix(self.message.split(" ")[0], self.prefix)
        self.raw_args =
        self.args = []
        self.kwargs = {}
        self.channel = bot.channels[event.target]

    def __str__(self):
        return "Context(Bot: {}, Prefix: {}, Message: {}, Command: {}, Arguments: {}, Server: {}, Channel: {})".format(
            self.bot, self.prefix, self.message, self.command, self.arguments, self.server, self.channel
        )

    def send(self, message):
        self.channel.send(message)


class Command:

    def __init__(self, name, callback, **attrs):
        self.name = name
        if not isinstance(name, str):
            raise TypeError('Name of a command must be a string.')
        self.callback = callback
        self.active = attrs.get("active", True)
        self.hidden = attrs.get("hidden", False)
        self.aliases = attrs.get("aliases", [])
        signature = inspect.signature(callback)
        self.params = signature.parameters.copy()

    def _parse_arguments(self, ctx):


    def invoke(self, ctx):
        if not self.can_run(ctx):
            return
        try:
            self.callback(ctx)
        except Exception as e:
            log.warning(e)

    def can_run(self, ctx):
        return self.active


def command(name=None, cls=None, **attrs):
    if cls is None:
        cls = Command

    def decorator(func):
        if isinstance(func, Command):
            raise TypeError("Function is already a Command")

        help_doc = attrs.get('help')
        if help_doc is not None:
            help_doc = inspect.cleandoc(help_doc)
        else:
            help_doc = inspect.getdoc(func)
            if isinstance(help_doc, bytes):
                help_doc = help_doc.decode('utf-8')

        attrs['help'] = help_doc

        cname = name or func.__name__
        return cls(name=cname, callback=func, **attrs)

    return decorator
