"""
    Talos for Discord
    A python based bot for discord, good for writing and a couple of minor shenanigans.

    Author: CraftSpider
"""
import discord
from discord.ext import commands
import traceback
import sys
import asyncio
import json
import logging
from datetime import datetime
from datetime import timedelta

#
#   Constants
#

# Current Talos version. Loosely incremented.
VERSION = "2.3.1"
# Time Talos started
BOOT_TIME = datetime.now()
# Extensions to load on Talos boot. Extensions for Talos should possess 'ops', 'perms', and 'options' variables.
STARTUP_EXTENSIONS = ["Commands", "UserCommands", "AdminCommands", "JokeCommands"]
# Talos saves its data in this file. Don't touch it unless you understand what you're doing.
SAVE_FILE = "./TalosData.dat"
# Default options for a new server. Don't touch it unless you understand what you're doing.
DEFAULT_OPTIONS = "./DefaultOptions.dat"
# Place your token in a file with this name, or change this to the name of a file with the token in it.
TOKEN_FILE = "Token.txt"

#
#   Command Vars
#

# Ops list. Filled on bot load, altered through the add and remove op commands.
ops = {}
# Permissions list. Filled on bot load, altered by command
perms = {}
# Options list. Filled on bot load, altered by command.
options = {}
# Default Options. Only used in Talos Base for setting up options for servers.
default_options = {}

# Initiate Logging
logging.basicConfig(level=logging.INFO)


class Talos(commands.Bot):
    """Class for the Talos bot. Handles all sorts of things for inter-cog relations and bot wide data."""

    VERSION = VERSION
    BOOT_TIME = BOOT_TIME
    # List of times when the bot was verified online.
    uptime = []

    def __init__(self, **args):
        description = '''Greetings. I'm Talos, chat helper. My commands are:'''
        super().__init__("^", description=description, **args)
        self.bg_task = self.loop.create_task(self.uptime_task())

    def load_extensions(self, extensions=None):
        """Loads all extensions in input, or all Talos extensions defined in STARTUP_EXTENSIONS if array is None."""
        for extension in (STARTUP_EXTENSIONS if extensions is None else extensions):
            try:
                self.load_extension(extension)
            except Exception as err:
                exc = '{}: {}'.format(type(err).__name__, err)
                logging.info('Failed to load extension {}\n{}'.format(extension, exc))

    def unload_extensions(self, extensions=None):
        """Unloads all extensions in input, or all extensions currently loaded if None"""
        if extensions is None:
            while len(self.extensions) > 0:
                bot.unload_extension(self.extensions[0])
        else:
            for extension in extensions:
                bot.unload_extension(extension)

    @staticmethod
    def get_default(option):
        return default_options[option]

    async def save(self):
        """Saves current talos data to the save file"""
        json_save(SAVE_FILE, ops=ops, perms=perms, options=options, uptime=self.uptime)

    async def logout(self):
        """Saves Talos data, then logs out the bot cleanly and safely"""
        await self.save()
        await super().logout()

    async def update(self, newOps=None, newPerms=None, newOptions=None):
        """
        Given a new set of values for ops, perms, or options, update Talos base and all extensions with those values.
        """
        if newOps:
            ops.update(newOps)
            for extension in bot.extensions:
                bot.extensions[extension].ops.update(newOps)
        if newPerms:
            perms.update(newPerms)
            for extension in bot.extensions:
                bot.extensions[extension].perms.update(newPerms)
        if newOptions:
            options.update(newOptions)
            for extension in bot.extensions:
                bot.extensions[extension].options.update(newOptions)
        await self.save()

    async def verify(self):
        """
        Verify current Talos data to ensure no guilds are missing values and that no values exist without guilds.
        Returns number of added and removed values.
        """
        added = 0
        removed = 0
        for guild in self.guilds:
            guild_id = str(guild.id)
            try:
                ops[guild_id]
            except KeyError:
                ops[guild_id] = {}
                added += 1
            try:
                perms[guild_id]
            except KeyError:
                perms[guild_id] = {}
                added += 1
            try:
                options[guild_id]
            except KeyError:
                options[guild_id] = default_options.copy()
                added += 1
            else:
                for key in default_options:
                    try:
                        options[guild_id][key]
                    except KeyError:
                        options[guild_id][key] = default_options[key]
                        added += 1
        obsolete = []
        for key in ops:
            check = False
            for guild in self.guilds:
                guild_id = str(guild.id)
                if key == guild_id:
                    check = True
            if not check:
                obsolete.append(key)
        for key in obsolete:
            logging.info("Cleaning ops for {}".format(key))
            del ops[key]
            removed += 1
        obsolete = []
        for key in perms:
            check = False
            for guild in self.guilds:
                guild_id = str(guild.id)
                if key == guild_id:
                    check = True
            if not check:
                obsolete.append(key)
        for key in obsolete:
            logging.info("Cleaning perms for {}".format(key))
            del perms[key]
            removed += 1
        obsolete = []
        for key in options:
            check = False
            for guild in self.guilds:
                guild_id = str(guild.id)
                if key == guild_id:
                    check = True
            if not check:
                obsolete.append(key)
        for key in obsolete:
            logging.info("Cleaning options for {}".format(key))
            del options[key]
            removed += 1
        await self.update(newOps=ops, newPerms=perms, newOptions=options)
        await self.save()
        return added, removed

    async def uptime_task(self):
        """Called once a minute, to verify uptime. Also removes old values from the list."""
        logging.info("Starting uptime task")
        delta = datetime.now().replace(minute=(datetime.now().minute + 1), second=0, microsecond=0) -\
            datetime.now().replace(microsecond=0)
        await asyncio.sleep(delta.total_seconds())
        while True:
            self.uptime.append(datetime.now().replace(microsecond=0).timestamp())
            old = []
            for item in self.uptime:
                if datetime.fromtimestamp(item) < datetime.now() - timedelta(days=30):
                    old.append(item)
            for item in old:
                self.uptime.remove(item)
            await self.save()
            await asyncio.sleep(60)

    async def on_ready(self):
        """Called on bot ready, any time discord finishes connecting"""
        print('| Now logged in as')
        print('| {}'.format(self.user.name))
        print('| {}'.format(self.user.id))
        await bot.change_presence(game=discord.Game(name="Taking over the World", type=0))

    async def on_guild_join(self, guild):
        """Called upon Talos joining a guild. Populates ops, perms, and options"""
        logging.info("Joined Guild {}".format(guild.name))
        guild_id = str(guild.id)
        ops[guild_id] = []
        perms[guild_id] = {}
        options[guild_id] = default_options.copy()
        await self.save()

    async def on_guild_remove(self, guild):
        """Called upon Talos leaving a guild. Populates ops, perms, and options"""
        logging.info("Left Guild {}".format(guild.name))
        guild_id = str(guild.id)
        del ops[guild_id]
        del perms[guild_id]
        del options[guild_id]
        await self.save()

    async def on_command_error(self, ctx, exception):
        """Called upon command error. Handles CommandNotFound and CheckFailure, other errors it simply logs"""
        if type(exception) == discord.ext.commands.CommandNotFound:
            if options[str(ctx.guild.id)]["FailMessage"]:
                await ctx.send("Sorry, I don't understand \"{}\". May I suggest ^help?".format(ctx.invoked_with))
        elif type(exception) == discord.ext.commands.CheckFailure:
            logging.info("Woah, {} tried to run a command without permissions!".format(ctx.author))
        else:
            print('Ignoring exception in command {}'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)


def string_load(filename):
    """Loads a file as an array of strings and returns that"""
    out = []
    with open(filename, 'a+') as file:
        try:
            file.seek(0)
            out = file.readlines()
        except Exception as e:
            print(e)
    return out


def load_token():
    """Loads the token file and returns the token"""
    file = string_load(TOKEN_FILE)
    return file[0].strip()


def json_load(filename):
    """Loads a file as a JSON object and returns that"""
    with open(filename, 'a+') as file:
        try:
            file.seek(0)
            data = json.load(file)
        except json.JSONDecodeError as e:
            logging.warning(e)
            data = None
    return data


def build_trees(data):
    """Builds Talos data from JSON read in from the save file"""
    try:
        ops.update(data['ops'])
        perms.update(data['perms'])
        options.update(data['options'])
        for extension in bot.extensions:
            bot.extensions[extension].ops.update(data['ops'])
            bot.extensions[extension].perms.update(data['perms'])
            bot.extensions[extension].options.update(data['options'])
    except KeyError as e:
        if str(e) in STARTUP_EXTENSIONS:
            logging.warning("Cog not loaded")
        else:
            logging.warning("Data didn't have key {}".format(e))


def json_save(filename, **kwargs):
    """Saves a file as valid JSON"""
    with open(filename, 'w+') as file:
        try:
            out = dict()
            for key in kwargs:
                out[key] = kwargs[key]
            json.dump(out, file, indent=2)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    bot = Talos()
    bot.load_extensions()

    try:
        json_data = json_load(SAVE_FILE)
        default_options = json_load(DEFAULT_OPTIONS)
        bot.uptime = json_data['uptime']
        if json_data is not None:
            build_trees(json_data)
        bot.run(load_token())
    finally:
        print("Talos Exiting")
