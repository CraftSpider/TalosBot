"""
    Talos for Discord
    A python based bot for discord, good for writing and a couple of minor shenanigans.

    Author: CraftSpider
"""
import discord
from discord.ext import commands
import traceback
import os
import sys
import asyncio
import json
import logging
import re
import httplib2
import random
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from datetime import datetime
from datetime import timedelta
from datetime import date
import argparse

flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

#
#   Constants
#

# Current Talos version. Loosely incremented.
VERSION = "2.3.1"
# Time Talos started
BOOT_TIME = datetime.now()
# Extensions to load on Talos boot. Extensions for Talos should possess 'ops', 'perms', and 'options' variables.
STARTUP_EXTENSIONS = ["Commands", "UserCommands", "JokeCommands", "AdminCommands"]
# Talos saves its data in this file. Don't touch it unless you understand what you're doing.
SAVE_FILE = "./TalosData.dat"
# Default options for a new server. Don't touch it unless you understand what you're doing.
DEFAULT_OPTIONS = "./DefaultOptions.dat"
# Place your token in a file with this name, or change this to the name of a file with the token in it.
TOKEN_FILE = "Token.txt"

# Google API values
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'TalosBot Prompt Reader'

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
logging.basicConfig(level=logging.INFO)


async def _talos_help_command(ctx, *commands: str):
    """Shows this message."""
    bot = ctx.bot

    if ctx.guild is not None:
        destination = ctx.message.author if (options[str(ctx.guild.id)]["PMHelp"]) else ctx.message.channel
    else:
        destination = ctx.message.channel

    def repl(obj):
        return _mentions_transforms.get(obj.group(0), '')

    # help by itself just lists our own commands.
    if len(commands) == 0:
        pages = await bot.formatter.format_help_for(ctx, bot)
    elif len(commands) == 1:
        # try to see if it is a cog name
        name = _mention_pattern.sub(repl, commands[0])
        command = None
        if name in bot.cogs:
            command = bot.cogs[name]
        else:
            command = bot.all_commands.get(name)
            if command is None:
                await destination.send(bot.command_not_found.format(name))
                return

        pages = await bot.formatter.format_help_for(ctx, command)
    else:
        name = _mention_pattern.sub(repl, commands[0])
        command = bot.all_commands.get(name)
        if command is None:
            await destination.send(bot.command_not_found.format(name))
            return

        for key in commands[1:]:
            try:
                key = _mention_pattern.sub(repl, key)
                command = command.all_commands.get(key)
                if command is None:
                    await destination.send(bot.command_not_found.format(key))
                    return
            except AttributeError:
                await destination.send(bot.command_has_no_subcommands.format(command, key))
                return

        pages = await bot.formatter.format_help_for(ctx, command)

    if bot.pm_help is None:
        characters = sum(map(lambda l: len(l), pages))
        # modify destination based on length of pages.
        if characters > 1000:
            destination = ctx.message.author

    for page in pages:
        await destination.send(page)


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials


credentials = get_credentials()
http = credentials.authorize(httplib2.Http())
discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl, cache_discovery=False)


def prefix(self, message):
    if isinstance(message.channel, discord.abc.PrivateChannel):
        return "^"
    else:
        try:
            return options[str(message.guild.id)]["Prefix"]
        except KeyError:
            return "^"


class Talos(commands.Bot):
    """Class for the Talos bot. Handles all sorts of things for inter-cog relations and bot wide data."""

    VERSION = VERSION
    BOOT_TIME = BOOT_TIME
    PROMPT_TIME = 10
    # List of times when the bot was verified online.
    uptime = []

    def __init__(self, **args):
        description = '''Greetings. I'm Talos, chat helper. My commands are:'''
        super().__init__(prefix, description=description, **args)
        self.remove_command("help")
        self.command(**self.help_attrs)(_talos_help_command)
        self.bg_tasks = []

    def start_tasks(self):
        self.bg_tasks.append(self.loop.create_task(self.uptime_task()))
        self.bg_tasks.append(self.loop.create_task(self.prompt_task()))

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

    @staticmethod
    def get_spreadsheet(sheet_id, sheet_range):
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=sheet_range).execute()
        return result.get('values', [])

    @staticmethod
    def set_spreadsheet(sheet_id, vals, sheet_range=None):
        body = {
            'values': vals
        }
        if sheet_range:
            result = service.spreadsheets().values().update(
                spreadsheetId=sheet_id, range=sheet_range,
                valueInputOption="RAW", body=body).execute()
        else:
            result = service.spreadsheets().values().append(
                spreadsheetId=sheet_id, range=sheet_range,
                valueInputOption="RAW", body=body).execute()
        return result

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
        delta = timedelta(seconds=60 - datetime.now().replace(microsecond=0).second)
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

    async def prompt_task(self):
        logging.info("Starting prompt task")
        now = datetime.now().replace(microsecond=0)
        delta = timedelta(hours=(24 - now.hour + (self.PROMPT_TIME-1)) % 24, minutes=60 - now.minute, seconds=60 - now.second)
        await asyncio.sleep(delta.total_seconds())
        while True:
            prompt_sheet_id = "1bL0mSDGK4ypn8wioQCBqkZH47HmYp6GnmJbXkIOg2fA"
            values = bot.get_spreadsheet(prompt_sheet_id, "Form Responses 1!B:E")
            possibilities = []
            values = list(values)
            for item in values:
                if len(item[3:]) == 0:
                    possibilities.append(item)
            prompt = random.choice(possibilities)

            out = "__Daily Prompt {}__\n\n".format(date.today().strftime("%m/%d"))
            out += "{}\n\n".format(prompt[0].strip("\""))
            out += "({} by {})".format(("Original prompt" if prompt[1] is "Yes" else "Submitted"), prompt[2])
            for guild in bot.guilds:
                for channel in guild.channels:
                    if channel.name == options[str(guild.id)]["PromptsChannel"]:
                        if options[str(guild.id)]["WritingPrompts"]:
                            await channel.send(out)

            prompt.append("POSTED")
            bot.set_spreadsheet(prompt_sheet_id, [prompt],
                                "Form Responses 1!B{0}:E{0}".format(values.index(prompt) + 1))
            await asyncio.sleep(24*60*60)

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
        bot.start_tasks()
        bot.run(load_token())
    finally:
        print("Talos Exiting")
