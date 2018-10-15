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
import pathlib
import mysql.connector
import datetime as dt
import utils.command_lang as command_lang
import utils
import utils.dutils as dutils

#
#   Constants
#

# Place your token in a file with this name, or change this to the name of a file with the token in it.
TOKEN_FILE = pathlib.Path(__file__).parent / "token.json"
FILE_BASE = {
    "token": "", "botlist": "", "nano": ["user", "pass"], "btn": "", "cats": "", "sql": ["user", "pass", "schema"]
}

#
#   Command Vars
#

# Help make it so mentions in the text don't actually mention people
_mentions_transforms = {
    '@everyone': '@\u200beveryone',
    '@here': '@\u200bhere'
}
_mention_pattern = re.compile('|'.join(_mentions_transforms.keys()))

_log_event_colors = {
    "kick": discord.Colour(int("fcd116", 16)),
    "ban": discord.Colour.red(),
    "silence": discord.Colour.dark_blue()
}

# Initiate Logging
log = logging.getLogger("talos")


class FakeMessage:
    def __init__(self, guild, channel):
        self.guild = guild
        self.channel = channel
        self.author = None


class Talos(commands.Bot):
    """
        Class for the Talos bot. Handles all sorts of things for inter-cog relations and bot wide data.
    """

    # Current Talos version. Loosely incremented.
    VERSION = "2.8.0"
    # Time Talos started
    BOOT_TIME = dt.datetime.utcnow()
    # Time, in UTC, that the prompt task kicks off each day.
    PROMPT_TIME = 10
    # Default Prefix, in case the options are unavailable.
    DEFAULT_PREFIX = "^"
    # Folder which extensions are stored in
    EXTENSION_DIRECTORY = "discord_talos.cogs"
    # Extensions to load on Talos boot. Can be standard discord.py extensions, though Talos also allows some more stuff.
    STARTUP_EXTENSIONS = ("commands", "user_commands", "joke_commands", "admin_commands", "dev_commands", "event_loops")
    # Hardcoded Developer List. Craft, Dino, Hidd, Hidd
    DEVS = (101091070904897536, 312902614981410829, 321787962935214082, 199856712860041216)
    # This is the address for a MySQL server for Talos. Without a server found here, Talos data storage won't work.
    SQL_ADDRESS = "127.0.0.1:3306"

    def __init__(self, **kwargs):
        """
            Initialize Talos object. Safe to pass nothing in.
        :param sql_conn: MySQL Database connection object
        :param kwargs: Keyword Args for Talos and all its parent classes
        :return: None
        """
        # Set default values to pass to super
        description = '''Greetings. I'm Talos, chat helper. Here are my command types. If you like me and have the \
money, please support me on [Patreon](https://www.patreon.com/TalosBot)'''
        if not kwargs.get("formatter", None):
            kwargs["formatter"] = kwargs.get("formatter", utils.TalosFormatter())
        super().__init__(talos_prefix, description=description, **kwargs)

        # Set talos specific things
        self.__tokens = kwargs.get("tokens", {})
        self.botlist = self.__tokens.get("botlist", "")  # TODO: make this more elegant for event loops

        sql = self.SQL_ADDRESS.split(":")
        address, port = sql[0], int(sql[1])
        self.database = utils.TalosDatabase(address, port, *self.__tokens.get("sql"))
        nano_login = self.__tokens.get("nano", ["", ""])
        btn_key = self.__tokens.get("btn", "")
        cat_key = self.__tokens.get("cat", "")
        self.session = utils.TalosHTTPClient(nano_login=nano_login, btn_key=btn_key, cat_key=cat_key, read_timeout=60,
                                             loop=self.loop)

        # Override things set by super init that we don't want
        self._skip_check = self.skip_check
        self.remove_command("help")
        self.command(name="help", aliases=["man"], description="Shows this message")(self._talos_help_command)

    def __setattr__(self, key, value):
        if key == key.upper():
            log.warning(f"Attempt to set Talos attribute: {key} {value}")
        else:
            super().__setattr__(key, value)

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
                log.debug(f"Loading extension {extension}")
                self.load_extension(extension)
            except Exception as err:
                clean = 1
                exc = f"{type(err).__name__}: {err}"
                log.warning(f"Failed to load extension {extension}\n{exc}")
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
                log.debug(f"Unloading extension {extension}")
                self.unload_extension(extension, False)
        else:
            for extension in extensions:
                log.debug(f"Unloading extension {extension}")
                self.unload_extension(extension)

    def load_extension(self, name, prefix=True):
        name = self.EXTENSION_DIRECTORY + "." + name if prefix else name
        super().load_extension(name)

    def unload_extension(self, name, prefix=True):
        name = self.EXTENSION_DIRECTORY + "." + name if prefix else name
        super().unload_extension(name)

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
            try:
                if not self.database.get_user_options(ctx.author.id).rich_embeds:
                    return False
                if ctx.guild is not None:
                    return self.database.get_guild_options(ctx.guild.id).rich_embeds and\
                           ctx.channel.permissions_for(ctx.me).embed_links
            except mysql.connector.ProgrammingError:
                return False
        return ctx.channel.permissions_for(ctx.me).embed_links

    def get_timezone(self, ctx):
        """
            Returns a timezone object with the offset to use for the given context.
        :param ctx: commands.Context object
        :return: Timezone object for the context
        """
        if self.database.is_connected():
            if ctx.guild is not None:
                timezone = self.database.get_guild_options(ctx.guild.id).timezone
                return dt.timezone(dt.timedelta(hours=utils.tz_map[timezone.upper()]), timezone.upper())
        return dt.timezone(dt.timedelta(), "UTC")

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

    def run(self, token, *args, **kwargs):
        """
            Run Talos. Logs into discord and runs event loop forever.
        :param token: Discord bot token to log in with
        :return: None
        """
        if self.cogs.get("EventLoops", None) is not None:
            self.cogs["EventLoops"].start_all_tasks()
        super().run(token, *args, **kwargs)

    async def logout(self):
        """
            Saves Talos data, then logs out the bot cleanly and safely
            :return None:
        """
        log.debug("Logging out Talos")
        self.database.commit()
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
            destination = ctx.message.author if self.database.get_guild_options(ctx.guild.id).pm_help else \
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
            elif name.capitalize() in self.cogs:
                command = self.cogs[name.capitalize()]
            else:
                command = self.all_commands.get(name)
                if command is None:
                    # Command not found always sent to invoke location
                    await ctx.send(self.command_not_found.format(name))
                    return

            pages = await self.formatter.format_help_for(ctx, command)
        elif ''.join(map(str.capitalize, args)) in self.cogs:
            command = self.cogs[''.join(map(str.capitalize, args))]
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

    async def process_commands(self, message):
        """
            Processes incoming messages from Discord, generates a ctx and invokes it.
        :param message: Message to process
        """
        ctx = await self.get_context(message)

        # Check for custom command
        if ctx.command is None and message.guild is not None:
            try:
                text = self.database.get_guild_command(message.guild.id, ctx.invoked_with).text
            except mysql.connector.Error:
                text = None
            except AttributeError:
                text = None
            ctx.command = custom_creator(ctx.invoked_with, text) if text is not None else text

        await self.invoke(ctx)

    async def mod_log(self, ctx, event, user, message):
        """
            Logs a message to a guild's mod log, if Talos is set up to do so
        :param ctx: Context object so we can know the guild
        :param event: Name of the event being logged
        :param user: User who is the target of the event
        :param message: The reason or details associated with the action
        """
        if not self.database.get_guild_options(ctx.guild.id).mod_log:
            return False
        if self.should_embed(ctx):
            with dutils.PaginatedEmbed() as embed:
                embed.title = event.capitalize()
                embed.colour = _log_event_colors.get(event, discord.Colour.purple())
                embed.add_field(name="User", value=str(user), inline=True)
                embed.add_field(name="Madmin", value=str(ctx.author), inline=True)
                embed.add_field(name="Reason", value=message)
            for page in embed.pages:
                await ctx.send(embed=page)
        else:
            out = f"{event.capitalize()}"
            out += f"User: {str(user)}"
            out += f"Madmin: {str(ctx.author)}"
            out += f"Reason: {message}"
            await ctx.send(out)

    async def on_ready(self):
        """
            Called on bot ready, any time discord finishes connecting
        :return: None
        """
        log.debug("OnReady Event")
        log.info("| Now logged in as")
        log.info(f"| {self.user.name}")
        log.info(f"| {self.user.id}")
        await self.change_presence(activity=discord.Game(name="Taking over the World", type=0))
        if self.__tokens.get("botlist") != "":
            log.info("Posting guilds to Discordbots")
            guild_count = len(self.guilds)
            self.cogs["EventLoops"].last_guild_count = guild_count
            headers = {
                'Authorization': self.__tokens["botlist"]}
            data = {'server_count': guild_count}
            api_url = 'https://discordbots.org/api/bots/199965612691292160/stats'
            await self.session.post(api_url, data=data, headers=headers)

    async def on_guild_join(self, guild):
        """
            Called upon Talos joining a guild.
        :param guild: discord.Guild object
        :return: None
        """
        log.debug("OnGuildJoin Event")
        log.info(f"Joined Guild {guild.name}, {dt.datetime.now() - self.BOOT_TIME} after boot")

    async def on_guild_remove(self, guild):
        """
            Called upon Talos leaving a guild.
        :param guild: discord.Guild object
        :return: None
        """
        log.debug("OnGuildRemove Event")
        log.info(f"Left Guild {guild.name}, {dt.datetime.now() - self.BOOT_TIME} after boot")
        self.database.clean_guild(guild.id)

    async def on_member_ban(self, guild, user):
        """
            Called upon a member being banned from a guild
        :param guild: Guild the user was banned from
        :param user: User who was banned
        """
        options = self.database.get_guild_options(guild.id)
        if not options.mod_log:
            return
        channel = list(filter(lambda x: x.name == options.log_channel, guild.channels))
        if channel:
            channel = channel[0]
            ctx = commands.Context()
            ctx.message = FakeMessage(guild, channel)
            await self.mod_log(ctx, "ban", user, "User banned for unknown reason")

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
            if self.database.is_connected() and (ctx.guild is None or
                                                 self.database.get_guild_options(ctx.guild.id).fail_message):
                cur_pref = (await self.get_prefix(ctx.message))[0]
                await ctx.send(f"Sorry, I don't understand \"{ctx.invoked_with}\". May I suggest {cur_pref}help?")
        elif isinstance(exception, commands.BotMissingPermissions):
            await ctx.send("I lack the permissions to run that command.")
        elif isinstance(exception, commands.NoPrivateMessage):
            await ctx.send("This command can only be used in a guild. Apologies.")
        elif isinstance(exception, commands.CheckFailure):
            # log.info(f"Woah, {ctx.author} tried to run command {ctx.command} without permissions!")
            await ctx.send("You lack the permission to run that command.")
        elif isinstance(exception, commands.BadArgument):
            await ctx.send(exception)
        elif isinstance(exception, commands.MissingRequiredArgument):
            exception: commands.MissingRequiredArgument
            await ctx.send(f"Missing parameter `{exception.param}`")
        elif isinstance(exception, dutils.NotRegistered):
            await ctx.send(f"User {exception} isn't registered, command could not be executed.")
        elif isinstance(exception, dutils.CustomCommandError):
            await ctx.send(f"Malformed CommandLang syntax: {exception}")
        else:
            timestamp = int(dt.datetime.now().timestamp())
            log.warning(f"Ignoring exception `{exception}` in command {ctx.command}. Reference ID: {timestamp}")
            try:
                if ctx.author.id in self.DEVS:
                    await ctx.send(f"```{exception} | {timestamp}```")
                else:
                    await ctx.send(
                        "Unknown error in command. Please contact devs through `contact@talosbot.org` "
                        f"or by posting an issue on the github. Error timestamp: {timestamp}"
                    )
            except Exception as e:
                log.error(e)
            log.warning("".join(traceback.format_exception(type(exception), exception, exception.__traceback__)))


cl_parser = command_lang.DiscordCL()


def custom_creator(name, text):
    """
        Create a custom temporary command for Talos
    :param name: Name of the invoked command
    :param text: Text of the command
    :return: commands.Command instance
    """

    async def custom_callback(ctx):
        try:
            out = cl_parser.parse_lang(ctx, text)
        except command_lang.CommandLangError as e:
            raise dutils.CustomCommandError(*e.args)
        if out.strip() != "":
            await ctx.send(out)

    return commands.Command(name, custom_callback)


def talos_prefix(bot, message):
    """
        Return the Talos prefix, given Talos class object and a message
    :param bot: Talos object to find prefix for
    :param message: Discord message object for context
    :return: List of valid prefixes for given bot and message
    """
    mention = bot.user.mention + " "
    if isinstance(message.channel, discord.abc.PrivateChannel):
        try:
            return [bot.database.get_user_options(message.author.id).prefix, mention]
        except Exception as e:
            log.warning("talos_prefix error: " + str(e))
            return [bot.DEFAULT_PREFIX, mention]
    else:
        try:
            return [bot.database.get_guild_options(message.guild.id).prefix, mention]
        except Exception as e:
            log.warning("talos_prefix error: " + str(e))
            return [bot.DEFAULT_PREFIX, mention]


def configure_logging():
    fh = logging.FileHandler(pathlib.Path(__file__).parent / "talos.log")
    sh = logging.StreamHandler(sys.stderr)

    ff = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
    sf = ff

    fh.setFormatter(ff)
    sh.setFormatter(sf)

    log.addHandler(fh)
    log.addHandler(sh)
    log.propagate = False
    log.setLevel(logging.INFO)

    dlog = logging.getLogger("discord")
    dlog.addHandler(fh)
    dlog.addHandler(sh)
    dlog.setLevel(logging.INFO)


def load_token_file(filename):
    """
        Loads a json token file for Talos
    :param filename: name of file to load
    :return: Dict with results of parsing file as json
    """
    out = {}
    import json
    try:
        with open(filename, 'r') as file:
            try:
                out = json.load(file)
            except Exception as ex:
                log.error(ex)
    except FileNotFoundError:
        log.error("Token file not found")
    return out


def make_token_file(filename):
    """
        Creates a token file with the given filename
    :param filename: name of file to create
    """
    import json
    with open(filename, "w") as file:
        json.dump(FILE_BASE, file)


def main():
    """
        Run Talos as main process. Say hello to our new robot overlord.
    :return: None
    """
    configure_logging()

    # Load Talos tokens
    tokens = load_token_file(TOKEN_FILE)
    if not tokens:
        log.fatal("Bot Token file missing, creating file and exiting")
        make_token_file(TOKEN_FILE)
        return 2

    bot_token = tokens.get("token")
    if not bot_token:
        log.fatal("Bot token missing, talos cannot start.")
        return 126
    if not tokens.get("botlist"):
        log.warning("Botlist token missing, stats will not be posted.")
    if not tokens.get("nano"):
        log.warning("Nano Login missing, nano commands will likely fail")
    if not tokens.get("btn"):
        log.warning("Behind The Name key missing, name commands will fail.")
    if not tokens.get("cat"):
        log.warning("TheCatAPI key missing, catpic command will fail.")

    # Create and run Talos
    talos = Talos(tokens=tokens)

    try:
        talos.load_extensions()
        talos.run(bot_token)
    finally:
        print("Talos Exiting")
    return 0


if __name__ == "__main__":
    exit(main())
