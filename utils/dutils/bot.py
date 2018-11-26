
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

    variable = ""

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
        if extensions is None:
            while len(self.extensions) > 0:
                extension = self.extensions.popitem()
                log.debug(f"Unloading extension {extension}")
                self.unload_extension(extension, False)
        else:
            for extension in extensions:
                log.debug(f"Unloading extension {extension}")
                self.unload_extension(extension)

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
            "name": "Talos",
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

    if isinstance(command, commands.Group):
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
        if not getattr(options, utils.to_snake_case(ctx.command.instance.__class__.__name__)):
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


class TalosCog:
    """Super class to all Talos cogs. Sets a default __local_check, and other init stuff."""

    __slots__ = ("bot", "database")

    def __new__(cls, bot):
        """Creates the instance of the current cog. Takes an instance of Talos to use while running."""
        local_name = f"_{cls.__name__}__local_check"
        if not hasattr(cls, local_name):
            setattr(cls, local_name, _perms_check)
        return super().__new__(cls)

    def __init__(self, bot):
        """Initiates the current cog. Takes an instance of Talos to use while running."""
        self.bot = bot
        self.database = None
        if hasattr(bot, "database"):
            self.database = bot.database


# TODO: rework this to be more consistent
class TalosFormatter(commands.HelpFormatter):
    """
        Talos help formatter. Fairly self explanatory.
    """

    def __init__(self, width=75):
        """
            Instantiate a new TalosFormatter object
        """
        self._paginator = None
        super().__init__(width)

    @property
    async def clean_prefix(self):
        """
            Returns the prefix from a context, cleaned up.
        :return: Clean prefix for the given context
        """
        return (await self.context.bot.get_prefix(self.context))[0]

    async def get_command_signature(self):
        """
            Retrieves the signature portion of the help page.
        :return: Command signature string
        """
        prefix = await self.clean_prefix
        cmd = self.command
        return prefix + cmd.signature

    async def get_ending_note(self):
        """
            Get the note to add on to the end of the help message
        :return: Note to end the help with
        """
        command_name = self.context.invoked_with
        return "Type `{0}{1} category` for a list of commands in a category.".format(
                   await self.clean_prefix, command_name
               )

    def embed_shorten(self, text):
        """
            Shorten a string to end with ellipsis if it is longer than the allowed width
        :param text: Text to bound
        :return: Text originally, or shortened with ellipsis if longer than width
        """
        if len(text) > self.width:
            return text[:self.width - 3] + '...\n'
        return text

    def _subcommands_field_value(self, _commands):
        """
            Get the value of the subcommands field for an embed from a given group command
        :param _commands: List of subcommands
        :return: String value of subcommands field in help
        """
        out = ""
        for name, command in _commands:
            if name in command.aliases:
                # skip aliases
                continue

            entry = '{0} - {1}\n'.format(name, command.description if command.description else "")
            shortened = self.embed_shorten(entry)
            out += shortened
        return out

    def _add_subcommands_to_page(self, max_width, _commands):
        """
            Add the subcommands field to a text page
        :param max_width: Maximum width of the help message
        :param _commands: List of subcommands
        """
        for name, command in _commands:
            if name in command.aliases:
                # skip aliases
                continue

            entry = '  {0:<{width}} {1}'.format(name, command.description if command.description else "",
                                                width=max_width)
            shortened = self.shorten(entry)
            self._paginator.add_line(shortened)

    async def format(self):
        """
            Run formatting on the current context and command
        :return: Result of formatting
        """
        if self.context.bot.should_embed(self.context):
            return await self.embed_format()
        else:
            return await self.string_format()

    async def embed_format(self):
        """
            Format an embed help message
        :return: Embed to post as result of formatting
        """
        self._paginator = paginators.PaginatedEmbed()

        description = self.command.description if not self.is_cog() else inspect.getdoc(self.command)

        if description:
            # <description> section
            self._paginator.description = description

        if isinstance(self.command, commands.Command):
            # <signature> section
            signature = await self.get_command_signature()
            self._paginator.add_field(name="Signature", value=signature)

            # <long doc> section
            if self.command.help:
                self._paginator.add_field(name="Documentation", value=self.command.help)

            # end it here if it's just a regular command
            if not self.has_subcommands():
                self._paginator.close()
                return self._paginator.pages

        filtered = await self.filter_command_list()
        if self.is_bot():
            self._paginator.title = "Talos Help"
            self._paginator.description = description+"\n"+await self.get_ending_note()

            for cog in self.command.cogs:
                if cog == "EventLoops" or cog == "DevCommands":
                    continue
                value = inspect.getdoc(self.command.cogs[cog])
                self._paginator.add_field(name=utils.add_spaces(cog), value=value)
        else:
            filtered = sorted(filtered)
            if filtered:
                value = self._subcommands_field_value(filtered)
                self._paginator.add_field(name='Commands', value=value)

        self._paginator.set_footer(text="Contact CraftSpider in the Talos discord (^info) for further help")
        self._paginator.close()
        return self._paginator.pages

    async def string_format(self):
        """
            Format a string help message
        :return: String to post as result of formatting
        """
        self._paginator = commands.Paginator()

        # we need a padding of ~80 or so

        description = self.command.description if not self.is_cog() else inspect.getdoc(self.command)

        if description:
            # <description> portion
            self._paginator.add_line(description, empty=True)

        if isinstance(self.command, commands.Command):
            # <signature portion>
            signature = await self.get_command_signature()
            self._paginator.add_line(signature, empty=True)

            # <long doc> section
            if self.command.help:
                self._paginator.add_line(self.command.help, empty=True)

            # end it here if it's just a regular command
            if not self.has_subcommands():
                self._paginator.close_page()
                return self._paginator.pages

        max_width = self.max_name_size

        def category(tup):
            cog = tup[1].cog_name
            # we insert the zero width space there to give it approximate
            # last place sorting position.
            return utils.add_spaces(cog) + ':' if cog is not None else '\u200bBase Commands:'

        filtered = await self.filter_command_list()
        if self.is_bot():
            data = sorted(filtered, key=category)
            for category, _commands in itertools.groupby(data, key=category):
                # there simply is no prettier way of doing this.
                _commands = sorted(_commands)
                if len(_commands) > 0:
                    self._paginator.add_line(category)

                self._add_subcommands_to_page(max_width, _commands)
        else:
            filtered = sorted(filtered)
            if filtered:
                self._paginator.add_line('Commands:')
                self._add_subcommands_to_page(max_width, filtered)

        # add the ending note
        self._paginator.add_line()
        ending_note = await self.get_ending_note()
        self._paginator.add_line(ending_note)
        return self._paginator.pages
