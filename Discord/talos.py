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
import datetime as dt

# try:
#     from .utils import TalosFormatter, TalosDatabase, TalosHTTPClient, NotRegistered, tz_map
# except SystemError or ImportError:
from utils import TalosFormatter, TalosDatabase, TalosHTTPClient, NotRegistered, tz_map

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
fh = logging.FileHandler("talos.log")
sh = logging.StreamHandler(sys.stderr)
logging.basicConfig(level=logging.INFO, handlers=[fh, sh])
log = logging.getLogger("talos")


class Talos(commands.Bot):
    """
        Class for the Talos bot. Handles all sorts of things for inter-cog relations and bot wide data.
    """

    # Current Talos version. Loosely incremented.
    VERSION = "2.6.0"
    # Time Talos started
    BOOT_TIME = dt.datetime.now()

    # Time, in UTC, that the prompt task kicks off each day.
    PROMPT_TIME = 10
    # Default Prefix, in case the options are unavailable.
    DEFAULT_PREFIX = "^"
    # Folder which extensions are stored in
    EXTENSION_DIRECTORY = "cogs"
    # Extensions to load on Talos boot. Can be standard discord.py extensions, though Talos also allows some more stuff.
    STARTUP_EXTENSIONS = ["commands", "user_commands", "joke_commands", "admin_commands", "dev_commands", "event_loops"]
    # Hardcoded Admin List. Craft, Dino, Hidd, Hidd
    ADMINS = (101091070904897536, 312902614981410829, 321787962935214082, 199856712860041216)
    # Discordbots bot list token
    discordbots_token = ""

    def __init__(self, sql_conn=None, **kwargs):
        """
            Initialize Talos object. Safe to pass nothing in.
        :param sql_conn: MySQL Database connection object
        :param kwargs: Keyword Args for Talos and all its parent classes
        :return: None
        """
        # Set default values to pass to super
        description = '''Greetings. I'm Talos, chat helper. Here are my commands.'''
        kwargs["formatter"] = kwargs.get("formatter", TalosFormatter())
        super().__init__(prefix, description=description, **kwargs)

        # Set talos specific things
        self.database = TalosDatabase(sql_conn)
        self.discordbots_token = kwargs.get("token", "")

        self.session = None

        # Override things set by super init that we don't want
        self._skip_check = self.skip_check
        self.remove_command("help")
        self.command(name="help", aliases=["man"], description="Shows this message")(self._talos_help_command)

    def load_extensions(self, extensions=None):
        """
            Loads all extensions in input, or all Talos extensions defined in STARTUP_EXTENSIONS if array is None.
            :param extensions: extensions to load, None if all in STARTUP_EXTENSIONS
            :return: 0 if successful, 1 if unsuccessful
        """
        log.debug("Loading all extensions")
        clean = 0
        for extension in (self.STARTUP_EXTENSIONS if extensions is None else extensions):
            try:
                log.debug("Loading extension {}".format(extension))
                self.load_extension(self.EXTENSION_DIRECTORY + "." + extension)
            except Exception as err:
                clean = 1
                exc = '{}: {}'.format(type(err).__name__, err)
                log.warning('Failed to load extension {}\n{}'.format(extension, exc))
        return clean

    def unload_extensions(self, extensions=None):
        """
            Unloads all extensions in input, or all extensions currently loaded if None
            :param extensions: List of extensions to unload, or None if all
        """
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
        """
            Determines whether Talos should skip trying to process a message
            :param author_id: integer ID of the message author
            :param self_id: integer ID of Talos client
            :return: Whether to skip processing a given message
        """
        if author_id == 339119069066297355 or author_id == 376161594570178562:
            return False
        return author_id == self_id or (self.get_user(author_id) is not None and self.get_user(author_id).bot)

    def should_embed(self, ctx):
        """
            Determines whether Talos is allowed to use RichEmbeds in a given context.
            :param ctx: commands.Context object
            :return: Whether Talos should embed message
        """
        if self.database.is_connected():
            if not self.database.get_user_option(ctx.author.id, "rich_embeds"):
                return False
            if ctx.guild is not None:
                return self.database.get_guild_option(ctx.guild.id, "rich_embeds") and\
                       ctx.channel.permissions_for(ctx.me).embed_links
        return ctx.channel.permissions_for(ctx.me).embed_links

    def get_timezone(self, ctx):
        """
            Returns a timezone object with the offset to use for the given context.
        :param ctx: commands.Context object
        :return: Timezone object for the context
        """
        if self.database.is_connected():
            if ctx.guild is not None:
                timezone = self.database.get_guild_option(ctx.guild.id, "timezone")
                return dt.timezone(dt.timedelta(hours=tz_map[timezone.upper()]), timezone.upper())
        return dt.timezone(dt.timedelta(), "UTC")

    async def logout(self):
        """
            Saves Talos data, then logs out the bot cleanly and safely
            :return None:
        """
        log.debug("Logging out Talos")
        await self.database.commit()
        await super().logout()

    async def close(self):
        """
            Closes connections that Talos has open on shutdown
            :return None:
        """
        log.debug("Closing Talos")
        await self.session.close()
        await super().close()

    async def _talos_help_command(self, ctx, *args: str):
        """The command you're using. Can show help for any command, cog, or extension Talos is running."""
        if ctx.guild is not None and self.database.is_connected():
            destination = ctx.message.author if self.database.get_guild_option(ctx.guild.id, "pm_help") else \
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

    def run(self, token, *args, **kwargs):
        """
            Run Talos. Logs into discord and runs event loop forever.
        :param token: Discord bot token to log in with
        :return: None
        """
        if self.cogs.get("EventLoops", None) is not None:
            self.cogs["EventLoops"].start_all_tasks()
        super().run(token, *args, **kwargs)

    async def start(self, *args, **kwargs):
        """
            Starts Talos. Opens the Talos session and passes on to super, which will login to discord and start the bot.
        :param args: non-keyword arguments
        :param kwargs: keyword arguments
        """
        nano_login = kwargs.get("nano_login", ["", ""])
        btn_key = kwargs.get("btn_key", "")
        log.info("Opened Talos HTTP Client")
        self.session = TalosHTTPClient(username=nano_login[0], password=nano_login[1], btn_key=btn_key,
                                       read_timeout=60, loop=self.loop)
        await super().start(*args, **kwargs)

    async def on_ready(self):
        """
            Called on bot ready, any time discord finishes connecting
        :return: None
        """
        log.debug("OnReady Event")
        log.info('| Now logged in as')
        log.info('| {}'.format(self.user.name))
        log.info('| {}'.format(self.user.id))
        await self.change_presence(game=discord.Game(name="Taking over the World", type=0))
        if self.discordbots_token != "":
            log.info("Posting guilds to Discordbots")
            guild_count = len(self.guilds)
            self.cogs["EventLoops"].last_guild_count = guild_count
            import aiohttp
            headers = {
                'Authorization': self.discordbots_token}
            data = {'server_count': guild_count}
            api_url = 'https://discordbots.org/api/bots/199965612691292160/stats'
            async with aiohttp.ClientSession() as session:
                await session.post(api_url, data=data, headers=headers)

    async def on_guild_join(self, guild):
        """
            Called upon Talos joining a guild. Populates ops, perms, and options
        :param guild: discord.Guild object
        :return: None
        """
        log.debug("OnGuildJoin Event")
        log.info("Joined Guild {}, {} after boot".format(guild.name, dt.datetime.now() - self.BOOT_TIME))

    async def on_guild_remove(self, guild):
        """
            Called upon Talos leaving a guild. Depopulates ops, perms, and options
        :param guild: discord.Guild object
        :return: None
        """
        log.debug("OnGuildRemove Event")
        log.info("Left Guild {}, {} after boot".format(guild.name, dt.datetime.now() - self.BOOT_TIME))

    async def on_command(self, ctx):
        """
            Called when any command is executed. Handles command tracking for users.
        :param ctx: commands.Context object
        :return: None
        """
        user = self.database.get_user(ctx.author.id)
        if user:
            self.database.user_invoked_command(ctx.author.id, str(ctx.command))

    async def on_command_error(self, ctx, exception):
        """
            Called upon command error. Handles most things that extend CommandError.
            any un-handled errors it simply logs
        :param ctx: commands.Context object
        :param exception: commands.CommandError child object
        :return: None
        """
        log.debug("OnCommandError Event")
        if isinstance(exception, commands.CommandNotFound):
            if self.database.is_connected() and self.database.get_guild_option(ctx.guild.id, "fail_message"):
                cur_pref = (await self.get_prefix(ctx.message))[0]
                await ctx.send("Sorry, I don't understand \"{}\". May I suggest {}help?".format(ctx.invoked_with,
                                                                                                cur_pref))
        elif isinstance(exception, commands.CheckFailure):
            log.info("Woah, {} tried to run command {} without permissions!".format(ctx.author, ctx.command))
        elif isinstance(exception, commands.NoPrivateMessage):
            await ctx.send("This command can only be used in a guild. Apologies.")
        elif isinstance(exception, commands.BadArgument):
            await ctx.send(exception)
        elif isinstance(exception, commands.MissingRequiredArgument):
            await ctx.send("Missing parameter `{}`".format(exception.param))
        elif isinstance(exception, NotRegistered):
            await ctx.send("User {} isn't registered, command could not be executed.".format(exception))
        else:
            log.warning('Ignoring exception in command {}'.format(ctx.command))
            traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)


def prefix(bot, message):
    """
        Return the Talos prefix, given Talos class object and a message
    :param bot: Talos object to find prefix for
    :param message: Discord message object for context
    :return: List of valid prefixes for given bot and message
    """
    mention = bot.user.mention + " "
    if isinstance(message.channel, discord.abc.PrivateChannel):
        try:
            return [bot.database.get_user_option(message.author.id, "prefix"), mention]
        except KeyError:
            return [bot.DEFAULT_PREFIX, mention]
    else:
        try:
            return [bot.database.get_guild_option(message.guild.id, "prefix"), mention]
        except KeyError:
            return [bot.DEFAULT_PREFIX, mention]


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
    """
        Loads the token file and returns the token
    :return: Talos client Token
    """
    file = string_load(TOKEN_FILE)
    return file[0].strip()


def load_botlist_token():
    """
        Load the discord-botlist token from the token file.
    :return: Talos discord botlist token
    """
    file = string_load(TOKEN_FILE)
    try:
        return file[1].strip()
    except KeyError:
        return ""


def load_nano_login():
    """
        Load the NaNoWriMo login info from the token file.
    :return: Talos NaNoWriMo login info
    """
    file = string_load(TOKEN_FILE)
    try:
        return file[2].strip().split(":")
    except KeyError:
        return []


def load_btn_key():
    """
        Load the BehindTheName key from the token file.
    :return: Talos BehindTheName token
    """
    file = string_load(TOKEN_FILE)
    try:
        return file[3].strip()
    except KeyError:
        return ""


def load_sql_data():
    """
        Load the SQL database login.
    :return:  Talos SQL login info, list.
    """
    file = string_load(TOKEN_FILE)
    try:
        return file[4].strip().split(":")
    except KeyError:
        return []


def main():
    """
        Run Talos as main process. Say hello to our new robot overlord.
    :return: None
    """
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

    btn_key = ""
    try:
        btn_key = load_btn_key()
    except IndexError:
        log.warning("Behind The Name key missing, name commands will fail.")

    # Load Talos database
    cnx = None
    try:
        sql = SQL_ADDRESS.split(":")
        login = load_sql_data()
        cnx = mysql.connector.connect(user=login[0], password=login[1], host=sql[0], port=int(sql[1]),
                                      database=login[2], autocommit=True)
        if cnx is None:
            log.warning("Talos database missing, no data will be saved this session.")
    except Exception as e:
        log.warning(e)
        log.warning("Database connection dropped, no data will be saved this session.")

    # Create and run Talos
    talos = Talos(sql_conn=cnx, token=botlist_token)

    try:
        talos.load_extensions()
        talos.run(bot_token, nano_login=nano_login, btn_key=btn_key)
    finally:
        print("Talos Exiting")
        cnx.commit()
        cnx.close()


if __name__ == "__main__":
    main()
