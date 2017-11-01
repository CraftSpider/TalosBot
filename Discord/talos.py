"""
    Talos for Discord
    A python based bot for discord, good for writing and a couple of minor shenanigans.

    Author: CraftSpider
"""
import discord
import discord.ext.commands as commands
import traceback
import sys
import logging
import re
import mysql.connector
from datetime import datetime

try:
    from .utils import TalosFormatter
    from .utils import TalosDatabase
    from .utils import TalosHTTPClient
except SystemError:
    from utils import TalosFormatter
    from utils import TalosDatabase
    from utils import TalosHTTPClient

#
#   Constants
#

# This is the address for a MySQL server for Talos. Without a server found here, Talos data storage won't work.
SQL_ADDRESS = "127.0.0.1:3306"
# Place your token in a file with this name, or change this to the name of a file with the token in it.
TOKEN_FILE = "Token.txt"

#
#   Command Vars
#

# Help make it so mentions in the text don't actually mention people
_mentions_transforms = {
    '@everyone': '@\u200beveryone',
    '@here': '@\u200bhere'
}
_mention_pattern = re.compile('|'.join(_mentions_transforms.keys()))

# Initiate Logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
log = logging.getLogger("talos")


def prefix(bot, message: discord.Message):
    """Return the Talos prefix, given Talos class object and a message"""
    mention = bot.user.mention + " "
    if isinstance(message.channel, discord.abc.PrivateChannel):
        return [bot.DEFAULT_PREFIX, mention]
    else:
        try:
            return [bot.get_guild_option(message.guild.id, "prefix"), mention]
        except KeyError:
            return [bot.DEFAULT_PREFIX, mention]


class Talos(commands.Bot, TalosDatabase):
    """Class for the Talos bot. Handles all sorts of things for inter-cog relations and bot wide data."""

    # Current Talos version. Loosely incremented.
    VERSION = "2.4.0"
    # Time Talos started
    BOOT_TIME = datetime.now()
    # Time, in UTC, that the prompt task kicks off each day.
    PROMPT_TIME = 10
    # Default Prefix, in case the options are borked.
    DEFAULT_PREFIX = "^"
    # Folder which extensions are stored in
    EXTENSION_DIRECTORY = "cogs"
    # Extensions to load on Talos boot. Extensions for Talos should possess 'ops', 'perms', and 'options' variables.
    STARTUP_EXTENSIONS = ["commands", "user_commands", "joke_commands", "admin_commands", "event_loops"]
    # Discordbots bot list token
    discordbots_token = ""

    def __init__(self, sql_conn=None, **args):
        """Initialize Talos object. Safe to pass nothing in."""
        # Set default values to pass to super
        description = '''Greetings. I'm Talos, chat helper. Here are my commands.'''
        args["formatter"] = args.get("formatter", TalosFormatter())
        super().__init__(prefix, description=description, **args)
        TalosDatabase.__init__(self, sql_conn)

        # Set talos specific things
        self.discordbots_token = args.get("token", "")
        nano_login = args.get("nano_login", ["", ""])

        async def open_session():
            log.info("Opened Talos HTTP Client")
            self.session = TalosHTTPClient(username=nano_login[0], password=nano_login[1])

        self.loop.create_task(open_session())

        # Override things set by super init that we don't want
        self._skip_check = self.skip_check
        self.remove_command("help")
        self.command(name="help", aliases=["man"])(self._talos_help_command)

    def load_extensions(self, extensions=None):
        """Loads all extensions in input, or all Talos extensions defined in STARTUP_EXTENSIONS if array is None."""
        logging.debug("Loading all extensions")
        for extension in (self.STARTUP_EXTENSIONS if extensions is None else extensions):
            try:
                log.debug("Loading extension {}".format(extension))
                self.load_extension(self.EXTENSION_DIRECTORY + "." + extension)
            except Exception as err:
                exc = '{}: {}'.format(type(err).__name__, err)
                log.warning('Failed to load extension {}\n{}'.format(extension, exc))

    def unload_extensions(self, extensions=None):
        """Unloads all extensions in input, or all extensions currently loaded if None"""
        logging.debug("Unloading all extensions")
        if extensions is None:
            while len(self.extensions) > 0:
                extension = self.extensions.popitem()
                log.debug("Unloading extension {}".format(extension))
                self.unload_extension(extension)
        else:
            for extension in extensions:
                log.debug("Unloading extension {}".format(extension))
                self.unload_extension(extension)

    def skip_check(self, author_id, self_id):
        """Determines whether Talos should skip trying to process a message"""
        if author_id == 339119069066297355:
            return False
        return author_id == self_id or (self.get_user(author_id) is not None and self.get_user(author_id).bot)

    @staticmethod
    def should_embed(ctx):
        """Determines whether Talos is allowed to use RichEmbeds in a given context."""
        if ctx.guild is not None:
            return ctx.bot.get_guild_option(ctx.guild.id, "rich_embeds") and\
                   ctx.channel.permissions_for(ctx.me).embed_links
        else:
            return ctx.channel.permissions_for(ctx.me).embed_links

    async def logout(self):
        """Saves Talos data, then logs out the bot cleanly and safely"""
        log.debug("Logging out")
        await self.commit()
        await super().logout()

    async def _talos_help_command(self, ctx, *args: str):
        """Shows this message."""
        if ctx.guild is not None:
            destination = ctx.message.author if self.get_guild_option(ctx.guild.id, "pm_help") else \
                          ctx.message.channel
        else:
            destination = ctx.message.channel

        def repl(obj):
            return _mentions_transforms.get(obj.group(0), '')

        # help by itself just lists our own commands.
        if len(args) == 0:
            pages = await self.formatter.format_help_for(ctx, self)
        elif len(args) == 1:
            # try to see if it is a cog name
            name = _mention_pattern.sub(repl, args[0])
            # command = None
            if name in self.cogs:
                command = self.cogs[name]
            else:
                command = self.all_commands.get(name)
                if command is None:
                    # Command not found always sent to invoke location
                    await ctx.send(self.command_not_found.format(name))
                    return

            pages = await self.formatter.format_help_for(ctx, command)
        else:
            name = _mention_pattern.sub(repl, args[0])
            command = self.all_commands.get(name)
            if command is None:
                # Command not found always sent to invoke location
                await ctx.send(self.command_not_found.format(name))
                return

            for key in args[1:]:
                try:
                    key = _mention_pattern.sub(repl, key)
                    command = command.all_commands.get(key)
                    if command is None:
                        await destination.send(self.command_not_found.format(key))
                        return
                except AttributeError:
                    await destination.send(self.command_has_no_subcommands.format(command, key))
                    return

            pages = await self.formatter.format_help_for(ctx, command)

        if self.pm_help is None:
            characters = sum(map(lambda l: len(l), pages))
            # modify destination based on length of pages.
            if characters > 1000:
                destination = ctx.message.author

        if destination == ctx.message.author:
            await ctx.send("I've DMed you some help.")
        for page in pages:
            if isinstance(page, discord.Embed):
                await destination.send(embed=page)
            else:
                await destination.send(page)

    def run(self, token):
        """Run Talos. Logs into discord and runs event loop forever."""
        if self.cogs.get("EventLoops", None) is not None:
            self.cogs["EventLoops"].start_all_tasks()
        super().run(token)

    async def on_ready(self):
        """Called on bot ready, any time discord finishes connecting"""
        log.debug("OnReady Event")
        log.info('| Now logged in as')
        log.info('| {}'.format(self.user.name))
        log.info('| {}'.format(self.user.id))
        await self.change_presence(game=discord.Game(name="Taking over the World", type=0))
        if self.discordbots_token != "":
            log.info("Posting guilds to Discordbots")
            guild_count = len(self.guilds)
            self.cogs["EventLoops"].last_server_count = guild_count
            import aiohttp
            headers = {
                'Authorization': self.discordbots_token}
            data = {'server_count': guild_count}
            api_url = 'https://discordbots.org/api/bots/199965612691292160/stats'
            async with aiohttp.ClientSession() as session:
                await session.post(api_url, data=data, headers=headers)

    async def on_guild_join(self, guild):
        """Called upon Talos joining a guild. Populates ops, perms, and options"""
        log.debug("OnGuildJoin Event")
        log.info("Joined Guild {}".format(guild.name))

    async def on_guild_remove(self, guild):
        """Called upon Talos leaving a guild. Depopulates ops, perms, and options"""
        log.debug("OnGuildRemove Event")
        log.info("Left Guild {}".format(guild.name))

    async def on_command_error(self, ctx, exception):
        """
        Called upon command error. Handles CommandNotFound, CheckFailure, and NoPrivateMessage.
        other errors it simply logs
        """
        log.debug("OnCommandError Event")
        if type(exception) == discord.ext.commands.CommandNotFound:
            if self.get_guild_option(ctx.guild.id, "fail_message"):
                cur_pref = (await self.get_prefix(ctx))[0]
                await ctx.send("Sorry, I don't understand \"{}\". May I suggest {}help?".format(ctx.invoked_with,
                                                                                                cur_pref))
        elif type(exception) == discord.ext.commands.CheckFailure:
            log.info("Woah, {} tried to run command {} without permissions!".format(ctx.author, ctx.command))
        elif type(exception) == discord.ext.commands.NoPrivateMessage:
            await ctx.send("This command can only be used in a server. Apologies.")
        else:
            log.warning('Ignoring exception in command {}'.format(ctx.command))
            traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)


def string_load(filename):
    """Loads a file as an array of strings and returns that"""
    out = []
    with open(filename, 'a+') as file:
        try:
            file.seek(0)
            out = file.readlines()
        except Exception as ex:
            log.error(ex)
    return out


def load_token():
    """Loads the token file and returns the token"""
    file = string_load(TOKEN_FILE)
    return file[0].strip()


def load_botlist_token():
    """Load the discord-botlist token from the token file."""
    file = string_load(TOKEN_FILE)
    try:
        return file[1].strip()
    except KeyError:
        return ""


def load_nano_login():
    file = string_load(TOKEN_FILE)
    try:
        return file[2].strip().split(":")
    except KeyError:
        return []


def main():
    # Load Talos tokens
    bot_token = ""
    try:
        bot_token = load_token()
    except IndexError:
        log.fatal("Bot token missing, talos cannot start.")
        exit(126)

    botlist_token = ""
    try:
        botlist_token = load_botlist_token()
    except IndexError:
        log.warning("Botlist token missing, stats will not be posted.")

    nano_login = []
    try:
        nano_login = load_nano_login()
    except IndexError:
        log.warning("Nano Login missing, nano commands will likely fail")

    # Load Talos files/databases
    cnx = None
    try:
        sql = SQL_ADDRESS.split(":")
        cnx = mysql.connector.connect(user="root", password="***REMOVED***", host=sql[0], port=int(sql[1]),
                                      database="talos_data", autocommit=True)
        if cnx is None:
            log.warning("Talos database missing, no data will be saved this session.")
    except Exception as e:
        log.warning(e)
        log.warning("Expected file or connection missing, new file created, connection dropped.")

    # Create and run Talos
    talos = Talos(sql_conn=cnx, token=botlist_token, nano_login=nano_login)

    try:
        talos.load_extensions()
        talos.run(bot_token)
    finally:
        print("Talos Exiting")
        cnx.commit()
        cnx.close()


if __name__ == "__main__":
    main()
