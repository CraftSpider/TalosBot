
import inspect
import logging
import itertools
import discord
import discord.ext.commands as commands

from .. import utils
from . import events
from . import paginators


log = logging.getLogger("talos.dutils.bot")


class ExtendedBot(commands.Bot):
    """
        Extends the functionality of d.py's Bot class. Adds in various helper methods, overrides some things to provide
        more functionality, and adds in support for EventLoops defined similarly to normal commands
    """

    def __init__(self, *args, **kwargs):
        """
            Initialize the bot. Sets up event loops and such stuff, will process any necessary args and kwargs
        :param args: List of arguments
        :param kwargs: List of keyword arguments
        """
        super().__init__(*args, **kwargs)

        self.all_events = {}

    # Extensions to super functionality

    def add_cog(self, cog):
        """
            Adds a cog to the bot. Calls through to super implementation, then adds on EventLoop handling.
        :param cog: instance of cog to add to the bot
        """
        super().add_cog(cog)

        for name, member in inspect.getmembers(cog):
            if isinstance(member, events.EventLoop):
                member.parent = cog
                self.add_event(member)

    def remove_cog(self, name):
        """
            Remove a cog from the bot. Calls through to super implementation after removing any EventLoops in the cog
        :param name: name of the cog to remove from the bot
        """
        cog = self.cogs.get(name, None)
        if cog is None:
            return

        for name, member in inspect.getmembers(cog):
            # remove events the cog has
            if isinstance(member, events.EventLoop):
                self.remove_event(member.name)

        super().remove_cog(name)

    def load_extension(self, name, prefix=True):
        """
            Load extension for the bot, adds in default prefix if the bot defines the `extension_dir` member
        :param name: Name of the extension to load
        :param prefix: Whether to add on a prefix if available
        """
        if prefix:
            extdir = getattr(self, "extension_dir")
            if extdir is not None:
                name = extdir + "." + name
        super().load_extension(name)

    def unload_extension(self, name, prefix=True):
        """
            Unload extension for the bot, adds in default prefix if the bot defines the `extension_dir` member
        :param name: Name of the extension to unload
        :param prefix: Whether to add on a prefix if available
        """
        if prefix:
            extdir = getattr(self, "extension_dir")
            if extdir is not None:
                name = extdir + "." + name
        super().unload_extension(name)

    def run(self, token, *args, **kwargs):
        """
            Run the bot. Loads `startup_extensions` if the member is defined, and starts all events
        :param token: Bot token to log in with
        :param args: Other arguments to supply to `start`
        :param kwargs: Other keyword arguments to supply to `start`
        """
        def_exts = getattr(self, "startup_extensions")
        if def_exts is not None:
            self.load_extensions(def_exts)
        for event in self.all_events:
            self.all_events[event].start()
        super().run(token, *args, **kwargs)

    # Event loop functions

    def add_event(self, event):
        """
            Add an event loop to the bot
        :param event: EventLoop object to add
        """
        if not isinstance(event, events.EventLoop):
            raise TypeError('The event passed must be a subclass of EventLoop')

        if event.name in self.all_events:
            raise discord.ClientException(f"Event {event.name} is already registered.")

        self.all_events[event.name] = event

    def remove_event(self, name):
        """
            Remove an event loop from the bot
        :param name: name of the EventLoop to remove
        :return: EventLoop object removed, or None if nothing matches the name
        """
        event = self.all_events.pop(name)
        if event is None:
            return None

        event.stop()
        event.parent = None

        return event

    # New helper methods

    def load_extensions(self, extensions):
        """
            Loads all extensions in input, or all Talos extensions defined in `startup_extensions` if array is None.
        :param extensions: extensions to load, None if all in `startup_extensions`
        :return: 0 if successful, otherwise number of extensions that failed to load
        """
        log.info("Loading multiple extensions")
        clean = 0
        for extension in extensions:
            try:
                log.debug(f"Loading extension {extension}")
                self.load_extension(extension)
            except Exception as err:
                clean += 1
                exc = f"{type(err).__name__}: {err}"
                log.warning(f"Failed to load extension {extension}\n{exc}")
        return clean

    def unload_extensions(self, extensions=None):
        """
            Unloads all extensions in input, or all extensions currently loaded if None
        :param extensions: List of extensions to unload, or None if all
        """
        log.info("Unloading multiple extensions")
        prefix = True
        if extensions is None:
            extensions = list(self.extensions.keys())
            prefix = False
        for extension in extensions:
            log.debug(f"Unloading extension {extension}")
            try:
                self.unload_extension(extension, prefix)
            except commands.ExtensionNotLoaded:
                pass

    def find_command(self, command):
        """
            Given a string command, attempts to find it iteratively through command groups
        :param command: Command to find in Talos. Can have spaces if necessary
        :return: Command object if found, None otherwise
        """
        if command in self.all_commands:
            return self.all_commands[command]
        command = command.split(" ")
        if len(command) > 1:
            cur = self
            for sub in command:
                cur = cur.all_commands.get(sub)
                if cur is None:
                    return None
            return cur
        return None

    def commands_dict(self):
        """
            Looks through all commands currently loaded into the bot, and converts them into a dictionary by group
            with their names, signatures, definitions, and any other desired metadata
        :return: dictionary of command definitions
        """
        out = {
            "name": self.__class__.__name__,
            "prefix": "^",
            "cogs": {
                "Base": {"name": "Base Commands", "description": "", "commands": []}
            }
        }
        for cog in self.cogs:
            cls = self.cogs[cog].__class__
            out["cogs"][cls.__name__] = {
                "name": utils.add_spaces(cls.__name__),
                "description": inspect.cleandoc(inspect.getdoc(cls)),
                "commands": []
            }
        for command in self.commands:
            cog = command.cog_name
            if cog is None:
                cog = "Base"
            _add_command(out["cogs"][cog], command)
        return out


def _add_command(data, command):
    """
        Adds a command to a dict in place, as passed in with `data`. Will run recursively if the command is a group
        with subcommands
    :param data: Dict to add the new command description dict to under the "commands" list
    :param command: Command to add to the data
    """
    new = {
        "name": command.name,
        "description": command.description,
        "help": command.help,
        "signature": command.signature,
        "aliases": command.aliases,
        "hidden": command.hidden,
        "commands": []
    }

    data["commands"].append(new)

    if isinstance(command, commands.GroupMixin):
        for com in command.commands:
            _add_command(new, com)


def _perms_check(self, ctx):
    """
        Determine whether the command can is allowed to run in this context.
    :param ctx: dcommands.Context object to consider
    :return: whether the command can run
    """
    if isinstance(ctx.channel, discord.abc.PrivateChannel) or ctx.author.id in self.bot.DEVS:
        return True
    command = str(ctx.command)

    try:
        options = self.bot.database.get_guild_options(ctx.guild.id)
        if not getattr(options, utils.to_snake_case(ctx.command.cog.__class__.__name__)):
            return False
    except KeyError:
        pass
    perms = self.bot.database.get_perm_rules(ctx.guild.id, command)
    if len(perms) == 0:
        return True
    perms.sort()
    for perm in perms:
        result = perm.get_allowed(ctx)
        if result is None:
            continue
        return result
    return True


class TalosCog(commands.Cog):
    """Super class to all Talos cogs. Sets a default __local_check, and other init stuff."""

    __slots__ = ("bot", "database")

    def __init__(self, bot):
        """Initiates the current cog. Takes an instance of Talos to use while running."""
        self.bot = bot
        self.database = None
        if hasattr(bot, "database"):
            self.database = bot.database

    cog_check = _perms_check


class TalosHelpCommand(commands.HelpCommand):
    """Talos default help command. Sends help as an embed, eventually should be able to send as text as well."""

    def get_destination(self):
        """
            Get where to send the help to. Checks the context for the bot and the database guild options
        :return: Messageable to send help to
        """
        ctx = self.context
        if ctx.guild is not None and ctx.bot.database.is_connected():
            if ctx.bot.database.get_guild_options(ctx.guild.id).pm_help:
                return ctx.author
            else:
                return ctx.channel
        else:
            return ctx.channel

    @property
    async def clean_prefix(self):
        """
            Returns the prefix from a context, cleaned up.
        :return: Clean prefix for the given context
        """
        return (await self.context.bot.get_prefix(self.context))[0]

    async def get_command_signature(self, command):
        """
            Retrieves the signature portion of the help page.
        :return: The signature of the given command
        """

        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = '|'.join(command.aliases)
            fmt = '[%s|%s]' % (command.name, aliases)
            if parent:
                fmt = parent + ' ' + fmt
            alias = fmt
        else:
            alias = command.name if not parent else parent + ' ' + command.name

        return '%s%s %s' % (await self.clean_prefix, alias, command.signature)

    async def get_starting_note(self):
        """
            Get the text that the help begins with
        :return: Note to end the help with
        """
        command_name = self.invoked_with
        return "Type `{0}{1} category` for a list of commands in a category.".format(
            await self.clean_prefix, command_name
        )

    def normalize_cog(self, bot, name):
        """
            Normalize the name of a cog, if the normalized form exists on the bot
        :param bot: Bot to test against
        :param name: Name to normalize
        :return: The original name, or the normalized form if it matches a cog
        """
        if name is None:
            return None
        normalized = utils.to_camel_case(name)
        if bot.get_cog(normalized) is not None:
            return normalized

    async def setup_paginator(self):
        """
            Prepare the output paginator for usage
        :return: The new setup paginator
        """
        paginator = paginators.PaginatedEmbed()

        paginator.title = "Talos Help"
        paginator.set_footer(text="Contact CraftSpider in the Talos discord (^info) for further help")

        return paginator

    async def send_bot_help(self, mapping):
        """
            Send the help for the whole bot, no sub-commands. Lists the available cogs
        :param mapping: Mapping of names to cogs
        """
        paginator = await self.setup_paginator()

        paginator.description = self.context.bot.description + "\n" + await self.get_starting_note()

        for cog in mapping:
            if cog is None:
                continue
            name = cog.qualified_name
            if name == "EventLoops" or name == "DevCommands":
                continue
            value = inspect.getdoc(cog)
            paginator.add_field(name=utils.add_spaces(name), value=value)

        dest = self.get_destination()
        paginator.close()
        for page in paginator.pages:
            await dest.send(embed=page)

    async def send_cog_help(self, cog):
        """
            Send help for a given cog. Lists the description and all non-hidden subcommands
        :param cog: The cog to send help for
        """
        paginator = await self.setup_paginator()

        paginator.description = cog.description

        text = ""
        for command in cog.get_commands():
            text += f"{command.name} - {command.description}\n"
        paginator.add_field(name="Commands", value=text)

        paginator.close()
        dest = self.get_destination()
        for page in paginator.pages:
            await dest.send(embed=page)

    async def send_command_help(self, command):
        """
            Send the help for a specific command, showing signature and extended description
        :param command: Command to send help for
        """
        paginator = await self.setup_paginator()

        paginator.description = command.description
        paginator.add_field(name="Signature", value=await self.get_command_signature(command))
        paginator.add_field(name="Documentation", value=command.help)

        paginator.close()
        dest = self.get_destination()
        for page in paginator.pages:
            await dest.send(embed=page)

    async def send_group_help(self, group):
        """
            Send the help for a specific command group, showing signature, extended description, and subcommands
        :param group: Group to send help for
        """
        paginator = await self.setup_paginator()

        paginator.description = group.description
        paginator.add_field(name="Signature", value=await self.get_command_signature(group))
        paginator.add_field(name="Documentation", value=group.help)

        text = ""
        for command in group.commands:
            text += f"{command.name} - {command.description}\n"
        paginator.add_field(name="Subcommands", value=text)

        paginator.close()
        dest = self.get_destination()
        for page in paginator.pages:
            await dest.send(embed=page)

    async def command_callback(self, ctx, *, command=None):
        """
            The actual running function for the help command. Not normally overriden, only overriden in this case to
            allow the use of the cog normalization
        :param ctx: Context of the help command
        :param command: Command, cog, bot or other object to send help for
        :return: Result of the parent callback
        """
        if not ctx.bot.should_embed(ctx):
            await ctx.send("Non-embed help command currently WIP")
            return

        cog_name = self.normalize_cog(ctx.bot, command)
        if cog_name is not None:
            command = cog_name

        return await super().command_callback(ctx, command=command)
