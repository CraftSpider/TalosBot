"""
    Talos for Discord
    A python based bot for discord, good for writing and a couple of minor shenanigans.

    Author: CraftSpider
"""
import discord
from discord.ext import commands
import traceback
import sys
import json
import logging
import re
from datetime import datetime
from collections import namedtuple

#
#   Constants
#

# Talos saves its data in this file. Don't touch it unless you understand what you're doing.
SAVE_FILE = "./TalosData.dat"
# Default options for a new server. Don't touch it unless you understand what you're doing.
DEFAULT_OPTIONS = "./DefaultOptions.json"
# Place your token in a file with this name, or change this to the name of a file with the token in it.
TOKEN_FILE = "Token.txt"


#
#   Command Vars
#

# Default Options. Only used in Talos Base for setting up options for servers.
default_options = {}
# Help make it so mentions in the text don't actually mention people
_mentions_transforms = {
    '@everyone': '@\u200beveryone',
    '@here': '@\u200bhere'
}
_mention_pattern = re.compile('|'.join(_mentions_transforms.keys()))

# Initiate Logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
log = logging.getLogger("talos")


def prefix(self , message: discord.Message):
    """Return the Talos prefix, given Talos class object and a message"""
    mention = self.user.mention + " "
    if isinstance(message.channel, discord.abc.PrivateChannel):
        return [self.DEFAULT_PREFIX, mention]
    else:
        try:
            return [talos.guild_data[str(message.guild.id)]["options"]["Prefix"], mention]
        except KeyError:
            return [self.DEFAULT_PREFIX, mention]


class Talos(commands.Bot):
    """Class for the Talos bot. Handles all sorts of things for inter-cog relations and bot wide data."""

    # Current Talos version. Loosely incremented.
    VERSION = "2.4.0"
    # Time Talos started
    BOOT_TIME = datetime.now()
    # Time, in UTC, that the prompt task kicks off each day.
    PROMPT_TIME = 10
    # Default Prefix, in case the options are borked.
    DEFAULT_PREFIX = "^"
    # Extensions to load on Talos boot. Extensions for Talos should possess 'ops', 'perms', and 'options' variables.
    STARTUP_EXTENSIONS = ["Commands", "UserCommands", "JokeCommands", "AdminCommands", "EventLoops"]
    # Fields that all servers should have in their data profile.
    SERVER_FIELDS = namedtuple('Fields', ["ops", "perms", "options"])(list, dict, default_options.copy)
    # Discordbots bot list token
    discordbots_token = ""
    # List of times when the bot was verified online.
    uptime = []
    # Server specific info dict. Form servers.guild_id.section.key
    guild_data = {}
    # User specific info dict. Form users.user_id.section.key
    user_data = {}

    def __init__(self, data=None, **args):
        """Initialize Talos object. Safe to pass nothing in."""
        description = '''Greetings. I'm Talos, chat helper. My commands are:'''
        if "token" in args:
            self.discordbots_token = args.pop("token")
        super().__init__(prefix, description=description, **args)
        self._skip_check = self.skip_check
        if data is not None:
            self.uptime = data.pop("uptime")
            if data.get("servers", "") == "":
                self.guild_data = data
            else:
                self.guild_data = data.pop("servers")
        self.remove_command("help")
        self.command(name="help", aliases=["man"])(self._talos_help_command)

    def load_extensions(self, extensions=None):
        """Loads all extensions in input, or all Talos extensions defined in STARTUP_EXTENSIONS if array is None."""
        logging.debug("Loading all extensions")
        for extension in (self.STARTUP_EXTENSIONS if extensions is None else extensions):
            try:
                log.debug("Loading extension {}".format(extension))
                self.load_extension(extension)
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
        if author_id == 339119069066297355:
            return False
        return author_id == self_id or (self.get_user(author_id) is not None and self.get_user(author_id).bot)

    @staticmethod
    def get_default(option):
        """Get the default value of an option"""
        return default_options[option]

    @staticmethod
    def should_embed(ctx):
        return ctx.bot.guild_data[str(ctx.guild.id)]["options"]["RichEmbeds"] and\
               ctx.channel.permissions_for(ctx.me).embed_links

    async def save(self):
        """Saves current talos data to the save file"""
        log.debug("saving data")
        json_save(SAVE_FILE, uptime=self.uptime, servers=self.guild_data)

    async def logout(self):
        """Saves Talos data, then logs out the bot cleanly and safely"""
        log.debug("logging out")
        await self.save()
        await super().logout()

    async def verify(self):
        """
        Verify current Talos data to ensure no guilds are missing values and that no values exist without guilds.
        Returns number of added and removed values.
        """
        added = 0
        removed = 0

        # Create missing values
        for guild in self.guilds:
            guild_id = str(guild.id)
            try:
                self.guild_data[guild_id]
            except KeyError:
                log.debug("Building {}".format(guild_id))
                self.guild_data[guild_id] = {}
                self.guild_data[guild_id]["ops"] = []
                self.guild_data[guild_id]["perms"] = {}
                self.guild_data[guild_id]["options"] = default_options.copy()
                added += 1
            else:
                for item in self.SERVER_FIELDS._fields:
                    try:
                        self.guild_data[guild_id][item]
                    except KeyError:
                        log.debug("Building {} for {}".format(item, guild_id))

                        self.guild_data[guild_id][item] = self.SERVER_FIELDS[item]()
                        added += 1
                    else:
                        if item != "options":
                            continue
                        for key in default_options:
                            try:
                                self.guild_data[guild_id]["options"][key]
                            except KeyError:
                                log.debug("Building option {} for {}".format(key, guild_id))
                                self.guild_data[guild_id]["options"][key] = default_options[key]
                                added += 1

        # Destroy unnecessary values
        obsolete = []
        for key in self.guild_data:
            check = False
            for guild in self.guilds:
                guild_id = str(guild.id)
                if key == guild_id:
                    check = True
            if not check:
                obsolete.append(key)
        for key in obsolete:
            log.info("Cleaning data for {}".format(key))
            del self.guild_data[key]
            removed += 1

        obsolete = []
        for guild in self.guild_data:
            for option in self.guild_data[guild]["options"]:
                if option not in default_options:
                    obsolete.append(option)
            break
        for guild in self.guild_data:
            for option in obsolete:
                log.info("Cleaning option {} for {}".format(option, guild))
                del self.guild_data[guild]["options"][option]
                removed += 1
        await self.save()
        return added, removed

    async def _talos_help_command(self, ctx, *args: str):
        """Shows this message."""
        if ctx.guild is not None:
            destination = ctx.message.author if (self.guild_data[str(ctx.guild.id)]["options"]["PMHelp"]) else \
                          ctx.message.channel
            if destination == ctx.message.author:
                await ctx.send("I've DMed you some help.")
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
                    await destination.send(self.command_not_found.format(name))
                    return

            pages = await self.formatter.format_help_for(ctx, command)
        else:
            name = _mention_pattern.sub(repl, args[0])
            command = self.all_commands.get(name)
            if command is None:
                await destination.send(self.command_not_found.format(name))
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

        for page in pages:
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
        added, removed = await self.verify()
        log.info("Added {} objects, Removed {} objects.".format(added, removed))
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
        guild_id = str(guild.id)
        self.guild_data[guild_id] = {}
        self.guild_data[guild_id]["ops"] = []
        self.guild_data[guild_id]["perms"] = {}
        self.guild_data[guild_id]["options"] = default_options.copy()
        await self.save()

    async def on_guild_remove(self, guild):
        """Called upon Talos leaving a guild. Populates ops, perms, and options"""
        log.debug("OnGuildRemove Event")
        log.info("Left Guild {}".format(guild.name))
        guild_id = str(guild.id)
        del self.guild_data[guild_id]
        await self.save()

    async def on_command_error(self, ctx, exception):
        """
        Called upon command error. Handles CommandNotFound, CheckFailure, and NoPrivateMessage.
        other errors it simply logs
        """
        log.debug("OnCommandError Event")
        if type(exception) == discord.ext.commands.CommandNotFound:
            if self.guild_data[str(ctx.guild.id)]["options"]["FailMessage"]:
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


def json_load(filename):
    """Loads a file as a JSON object and returns that"""
    with open(filename, 'a+') as file:
        try:
            file.seek(0)
            data = json.load(file)
        except json.JSONDecodeError:
            data = None
    return data


def json_save(filename, **kwargs):
    """Saves a file as valid JSON"""
    with open(filename, 'w+') as file:
        try:
            out = dict()
            for key in kwargs:
                out[key] = kwargs[key]
            json.dump(out, file, indent=2)
        except Exception as ex:
            print(ex)


if __name__ == "__main__":
    # Load Talos tokens
    bot_token = ""
    try:
        bot_token = load_token()
    except IndexError:
        log.fatal("Bot token missing, talos cannot start.")
        exit(66)

    botlist_token = ""
    try:
        botlist_token = load_botlist_token()
    except IndexError:
        log.warning("Botlist token missing, stats will not be posted.")

    # Load Talos files
    json_data = None
    try:
        json_data = json_load(SAVE_FILE)
        default_options = json_load(DEFAULT_OPTIONS)
        if default_options is None:
            log.fatal("Couldn't find default options, talos cannot start.")
            exit(66)
        if json_data is None:
            log.warning("Talos data missing, new data set will be created.")
    except Exception as e:
        log.warning(e)
        log.warning("Expected file missing, new file created.")

    # Create and run Talos
    talos = Talos(json_data, token=botlist_token)

    try:
        talos.load_extensions()
        talos.run(bot_token)
    finally:
        print("Talos Exiting")
        json_save(SAVE_FILE, uptime=talos.uptime, servers=talos.guild_data)
