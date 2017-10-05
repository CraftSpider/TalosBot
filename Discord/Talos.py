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

#
#   Constants
#

# Current Talos version. Loosely incremented.
VERSION = "2.4.0"
# Time Talos started
BOOT_TIME = datetime.now()
# Extensions to load on Talos boot. Extensions for Talos should possess 'ops', 'perms', and 'options' variables.
STARTUP_EXTENSIONS = ["Commands", "UserCommands", "JokeCommands", "AdminCommands", "EventLoops"]
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
# Help make it so mentions in the text don't actually mention people
_mentions_transforms = {
    '@everyone': '@\u200beveryone',
    '@here': '@\u200bhere'
}
_mention_pattern = re.compile('|'.join(_mentions_transforms.keys()))

# Initiate Logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logging = logging.getLogger("talos")


def prefix(self, message):
    if isinstance(message.channel, discord.abc.PrivateChannel):
        return self.DEFAULT_PREFIX
    else:
        try:
            return options[str(message.guild.id)]["Prefix"]
        except KeyError:
            return self.DEFAULT_PREFIX


class Talos(commands.Bot):
    """Class for the Talos bot. Handles all sorts of things for inter-cog relations and bot wide data."""

    VERSION = VERSION
    BOOT_TIME = BOOT_TIME
    PROMPT_TIME = 10
    DEFAULT_PREFIX = "^"
    # List of times when the bot was verified online.
    uptime = []

    def __init__(self, **args):
        description = '''Greetings. I'm Talos, chat helper. My commands are:'''
        super().__init__(prefix, description=description, **args)
        self.remove_command("help")
        self.command(name="help", aliases=["man"])(self._talos_help_command)

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
                self.unload_extension(self.extensions.popitem())
        else:
            for extension in extensions:
                self.unload_extension(extension)

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
            for extension in self.extensions:
                self.extensions[extension].ops.update(newOps)
        if newPerms:
            perms.update(newPerms)
            for extension in self.extensions:
                self.extensions[extension].perms.update(newPerms)
        if newOptions:
            options.update(newOptions)
            for extension in self.extensions:
                self.extensions[extension].options.update(newOptions)
        await self.save()

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
                ops[guild_id]
            except KeyError:
                logging.info("Building ops for {}".format(guild_id))
                ops[guild_id] = {}
                added += 1
            try:
                perms[guild_id]
            except KeyError:
                logging.info("Building perms for {}".format(guild_id))
                perms[guild_id] = {}
                added += 1
            try:
                options[guild_id]
            except KeyError:
                logging.info("Building options for {}".format(guild_id))
                options[guild_id] = default_options.copy()
                added += 1
            else:
                for key in default_options:
                    try:
                        options[guild_id][key]
                    except KeyError:
                        logging.info("Building option {} for {}".format(key, guild_id))
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
        obsolete = []
        for key in options:
            for option in options[key]:
                if option not in default_options:
                    obsolete.append(option)
            break
        for key in options:
            for option in obsolete:
                logging.info("Cleaning option {} for {}".format(option, key))
                del options[key][option]
                removed += 1
        await self.update(newOps=ops, newPerms=perms, newOptions=options)
        await self.save()
        return added, removed

    async def _talos_help_command(self, ctx, *args: str):
        """Shows this message."""
        if ctx.guild is not None:
            destination = ctx.message.author if (options[str(ctx.guild.id)]["PMHelp"]) else ctx.message.channel
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
            command = None
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

    async def on_ready(self):
        """Called on bot ready, any time discord finishes connecting"""
        logging.info('| Now logged in as')
        logging.info('| {}'.format(self.user.name))
        logging.info('| {}'.format(self.user.id))
        await self.change_presence(game=discord.Game(name="Taking over the World", type=0))
        added, removed = await self.verify()
        logging.info("Added {} objects, Removed {} objects.".format(added, removed))
        if __name__ == "__main__":
            self.cogs["EventLoops"].start_all_tasks()

    async def on_guild_join(self, guild):
        """Called upon Talos joining a guild. Populates ops, perms, and options"""
        logging.info("Joined Guild {}".format(guild.name))
        guild_id = str(guild.id)
        ops[guild_id] = []
        perms[guild_id] = {}
        options[guild_id] = default_options.copy()
        await self.update(newOps=ops, newPerms=perms, newOptions=options)
        await self.save()

    async def on_guild_remove(self, guild):
        """Called upon Talos leaving a guild. Populates ops, perms, and options"""
        logging.info("Left Guild {}".format(guild.name))
        guild_id = str(guild.id)
        del ops[guild_id]
        del perms[guild_id]
        del options[guild_id]
        await self.update(newOps=ops, newPerms=perms, newOptions=options)
        await self.save()

    async def on_command_error(self, ctx, exception):
        """Called upon command error. Handles CommandNotFound and CheckFailure, other errors it simply logs"""
        if type(exception) == discord.ext.commands.CommandNotFound:
            if options[str(ctx.guild.id)]["FailMessage"]:
                cur_pref = await self.get_prefix(ctx)
                await ctx.send("Sorry, I don't understand \"{}\". May I suggest {}help?".format(ctx.invoked_with,
                                                                                                cur_pref))
        elif type(exception) == discord.ext.commands.CheckFailure:
            logging.info("Woah, {} tried to run command {} without permissions!".format(ctx.author, ctx.command))
        elif type(exception) == discord.ext.commands.NoPrivateMessage:
            await ctx.send("This command can only be used in a server. Apologies.")
        else:
            logging.warning('Ignoring exception in command {}'.format(ctx.command))
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
            logging.warning(e.__name__, e)
            data = None
    return data


def build_trees(data):
    """Builds Talos data from JSON read in from the save file"""
    try:
        ops.update(data['ops'])
        perms.update(data['perms'])
        options.update(data['options'])
        for extension in talos.extensions:
            talos.extensions[extension].ops.update(data['ops'])
            talos.extensions[extension].perms.update(data['perms'])
            talos.extensions[extension].options.update(data['options'])
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
    talos = Talos()
    talos.load_extensions()

    try:
        json_data = json_load(SAVE_FILE)
        default_options = json_load(DEFAULT_OPTIONS)
        if default_options is None:
            logging.critical("Couldn't find default options")
            exit(1)
        if json_data is not None:
            talos.uptime = json_data['uptime']
            build_trees(json_data)
        talos.run(load_token())
    finally:
        print("Talos Exiting")
