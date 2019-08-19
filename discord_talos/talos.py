"""
    Talos for Discord
    A python based bot for discord, good for writing and a couple of minor shenanigans.

    Author: CraftSpider
"""

import discord
import discord.ext.commands as commands
import sys
import logging
import re
import pathlib
import mysql.connector
import datetime as dt
import spidertools.common as utils
import spidertools.discord as dutils
import spidertools.command_lang as command_lang
import discord_talos.talossql as sql

#
#   Constants
#

# Place your token in a file with this name, or change this to the name of a file with the token in it.
TOKEN_FILE = pathlib.Path(__file__).parent / "token.json"
FILE_BASE = {
    "token": "", "botlist": "", "nano": ["user", "pass"], "btn": "", "cat": "",
    "sql": {
        "address": "",
        "port": "",
        "username": "",
        "password": "",
        "schema": ""
    },
    "webserver": ""
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
    """Fake Message object used internally with Talos Mod Log"""

    __slots__ = ("guild", "channel", "author")

    def __init__(self, guild, channel):
        """
            Initialize fake message for given guild and channel
        :param guild: Guild the message relates to
        :param channel: Channel the event happened in
        """
        self.guild = guild
        self.channel = channel
        self.author = None


class Talos(dutils.ExtendedBot):
    """
        Class for the Talos bot. Handles all sorts of things for inter-cog relations and bot wide data.
    """

    # Current Talos version. Loosely incremented.
    VERSION = "2.9.0"
    # Time Talos started
    BOOT_TIME = dt.datetime.utcnow()
    # Time, in UTC, that the prompt task kicks off each day.
    PROMPT_TIME = 10
    # Default Prefix, in case the options are unavailable.
    DEFAULT_PREFIX = "^"
    # Folder which extensions are stored in
    extension_dir = "discord_talos.cogs"
    # Extensions to load on Talos boot. Can be standard discord.py extensions, though Talos also allows some more stuff.
    startup_extensions = ("commands", "user_commands", "joke_commands", "admin_commands", "dev_commands", "event_loops")
    # Hardcoded Developer List. Craft, Dino, Hidd
    DEVS = (101091070904897536, 312902614981410829, 199856712860041216)

    def __init__(self, **kwargs):
        """
            Initialize Talos object. Safe to pass nothing in.
        :param tokens: Dictionary of tokens for Talos to use
        :param kwargs: Keyword Args for Talos and all its parent classes
        """
        # Set default values to pass to super
        description = '''Greetings. I'm Talos, chat helper. Here are my command types. If you like me and have the \
money, please support me on [Patreon](https://www.patreon.com/CraftSpider)'''
        if kwargs.get("help_command", None) is None:
            kwargs["help_command"] = dutils.TalosHelpCommand()
        super().__init__(talos_prefix, description=description, **kwargs)

        # Set talos specific things
        __tokens = kwargs.get("tokens", {})
        with open("discord_talos/schema.json", "r") as file:
            import json
            schema_def = json.load(file)

        self.database = utils.TalosDatabase(**__tokens.get("sql"), schemadef=schema_def)
        self.session = utils.TalosHTTPClient(tokens=__tokens, read_timeout=60, loop=self.loop)

        # Override things set by super init that we don't want
        # self.remove_command("help")
        # self.command(name="help", aliases=["man"], description="Shows this message")(self._talos_help_command)

    def __setattr__(self, key, value):
        """
            Talos overloaded setattr. Prevents the changing of constants
        :param key: Name of attribute to set
        :param value: Value to set attribute to
        """
        if key == key.upper():
            log.warning(f"Attempt to set Talos attribute: {key} to {value}")
        else:
            super().__setattr__(key, value)

    def should_embed(self, ctx):
        """
            Determines whether Talos is allowed to use RichEmbeds in a given context.
        :param ctx: commands.Context object
        :return: Whether Talos should embed message
        """
        if self.database.is_connected():
            if not ctx.user_options.rich_embeds:
                return False
            if ctx.guild is not None:
                return ctx.guild_options.rich_embeds and\
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
                timezone = ctx.guild_options.timezone
                return dt.timezone(dt.timedelta(hours=utils.tz_map[timezone.upper()]), timezone.upper())
        return dt.timezone(dt.timedelta(), "UTC")

    async def logout(self):
        """
            Saves Talos data, then logs out the bot cleanly and safely
        """
        log.debug("Logging out Talos")
        self.database.commit()
        await super().logout()

    async def close(self):
        """
            Closes connections that Talos has open on shutdown
        """
        log.debug("Closing Talos")
        await self.session.close()
        await super().close()

    async def get_context(self, message, *, cls=commands.Context):
        """
            Create a new context from an incoming message, setting up attributes and etc
        :param message: Message to generate context from
        :param cls: Class to use for the context
        :return: new Context object
        """
        ctx = await super().get_context(message, cls=cls)

        if ctx.guild is not None:
            try:
                ctx.guild_options = self.database.get_guild_options(ctx.guild.id)
            except mysql.connector.Error:
                ctx.guild_options = None
                log.warning("Error getting guild options from database")
        else:
            ctx.guild_options = None

        try:
            ctx.user_options = self.database.get_user_options(ctx.author.id)
        except mysql.connector.Error:
            ctx.user_options = None
            log.warning("Error getting user options from database")

        # Check for custom command
        if ctx.command is None and message.guild is not None:
            try:
                command = self.database.get_item(sql.GuildCommand, guild_id=ctx.guild.id, name=ctx.invoked_with)
                if command is not None:
                    ctx.command = custom_creator(ctx.invoked_with, command.text)
            except mysql.connector.Error:
                pass

        return ctx

    async def process_commands(self, message):
        """
            Processes incoming messages from Discord, generates a ctx and invokes it.
        :param message: Message to process
        """
        if message.author.bot and not (message.author.id in (339119069066297355, 376161594570178562)):
            return

        ctx = await self.get_context(message)
        await self.invoke(ctx)

    async def mod_log(self, ctx, event, user, message):
        """
            Logs a message to a guild's mod log, if Talos is set up to do so
        :param ctx: Context object so we can know the guild
        :param event: Name of the event being logged
        :param user: User who is the target of the event
        :param message: The reason or details associated with the action
        """
        options = ctx.guild_options
        if not options.mod_log:
            return False
        try:
            logchan = next(filter(lambda x: x.name == options.log_channel, ctx.guild.channels))
        except StopIteration:
            await ctx.send("Invalid log channel, please set the `log_channel` option to a valid channel name")
            return
        if self.should_embed(ctx):
            with dutils.PaginatedEmbed() as embed:
                embed.title = event.capitalize()
                embed.colour = _log_event_colors.get(event, discord.Colour.purple())
                embed.add_field(name="User", value=str(user), inline=True)
                embed.add_field(name="Madmin", value=str(ctx.author), inline=True)
                embed.add_field(name="Reason", value=message)
            for page in embed.pages:
                await logchan.send(embed=page)
        else:
            out = f"{event.capitalize()}"
            out += f"User: {str(user)}"
            out += f"Madmin: {str(ctx.author)}"
            out += f"Reason: {message}"
            await logchan.send(out)

    async def on_ready(self):
        """
            Called on bot ready, any time discord finishes connecting
        """
        log.debug("OnReady Event")
        log.info("| Now logged in as")
        log.info(f"| {self.user.name}")
        log.info(f"| {self.user.id}")
        await self.change_presence(activity=discord.Game(name="Taking over the World", type=0))
        guild_count = len(self.guilds)
        await self.session.botlist_post_guilds(guild_count)

    async def on_guild_join(self, guild):
        """
            Called upon Talos joining a guild.
        :param guild: discord.Guild object
        """
        log.debug("OnGuildJoin Event")
        log.info(f"Joined Guild {guild.name}, {dt.datetime.now() - self.BOOT_TIME} after boot")

    async def on_guild_remove(self, guild):
        """
            Called upon Talos leaving a guild.
        :param guild: discord.Guild object
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
            ctx = commands.Context(message=FakeMessage(guild, channel))
            await self.mod_log(ctx, "ban", user, "User banned for unknown reason")

    async def on_command(self, ctx):
        """
            Called when any command is executed. Handles command tracking for users.
        :param ctx: commands.Context object
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
        """
        log.debug("OnCommandError Event")
        if isinstance(exception, commands.CommandNotFound):
            if ctx.guild is None or ctx.guild_options.fail_message:
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
            await ctx.send(f"Missing parameter `{exception.param}`")
        elif isinstance(exception, commands.UserInputError):
            await ctx.send(exception)
        elif isinstance(exception, dutils.NotRegistered):
            await ctx.send(f"User {exception} isn't registered, command could not be executed.")
        elif isinstance(exception, dutils.CustomCommandError):
            await ctx.send(f"Malformed CommandLang syntax: {exception}")
        else:
            timestamp = int(dt.datetime.now().timestamp())
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
            message = f"Ignoring exception `{exception}` in command {ctx.command}. Reference ID: {timestamp}"
            utils.log_error(log, logging.ERROR, exception, message)


runner = command_lang.CommandLang(interpreter=command_lang.DiscordCL())


def custom_creator(name, text):
    """
        Create a custom temporary command for Talos
    :param name: Name of the invoked command
    :param text: Text of the command
    :return: commands.Command instance
    """

    async def custom_callback(ctx):
        try:
            out = runner.exec(ctx, text)
        except command_lang.CommandLangError as e:
            raise dutils.CustomCommandError(*e.args)
        out = out.strip()
        if out != "":
            await ctx.send(out)

    return commands.Command(custom_callback, name=name)


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
    """
        Configure the loggers for Talos. Sets up the Talos loggers
        and discord.py loggers separately, so they can be easily configured
        independently.
    """
    fh = logging.FileHandler(utils.log_folder / "dtalos.log")
    dfh = logging.FileHandler(utils.log_folder / "dpy.log")
    sh = logging.StreamHandler(sys.stderr)
    gh = None
    try:
        import google.cloud.logging as glog
        client = glog.Client()
        gh = client.get_default_handler()
        gh.name = "dtalos"
        gh.setLevel(logging.WARNING)
    except (ImportError, OSError):
        pass

    ff = logging.Formatter("%(levelname)s:%(name)s:%(message)s")

    dlog = logging.getLogger("discord")

    utils.configure_logger(log, handlers=[fh, sh, gh], formatter=ff, level=logging.INFO, propagate=False)
    utils.configure_logger(dlog, handlers=[dfh, sh], formatter=ff, level=logging.INFO, propagate=False)


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
    :return: Exit status code
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
        talos.run(bot_token)
    except Exception as e:
        utils.log_error(log, logging.FATAL, e, "Talos shutting down due to unexpected error:")
    finally:
        log.info("Talos Exiting")
    return 0


if __name__ == "__main__":
    sys.exit(main())
