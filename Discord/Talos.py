"""
    Talos for Discord
    A python based bot for discord, good for writing and a couple of minor shenanigans.

    Author: CraftSpider
"""
import discord
import traceback
import sys
from discord.ext import commands
import json
import logging
import datetime
import asyncio
# from concurrent.futures import ThreadPoolExecutor
# import threading

#
#   Constants
#
VERSION = "2.2.1"
BOOT_TIME = datetime.datetime.now()
EGG_DEV = "wundrweapon#4856"
STARTUP_EXTENSIONS = ["Commands", "UserCommands", "AdminCommands"]
SAVE_FILE = "./TalosData.dat"

#
#   Command Vars
#
is_sleeping = 0
perms = {}


# Place your token in a file with this name, or change this to the name of a file with the token in it.
TOKEN_FILE = "Token.txt"

# Initiate Logging
logging.basicConfig(level=logging.INFO)


class Talos(commands.Bot):

    VERSION = VERSION
    BOOT_TIME = BOOT_TIME

    def __init__(self, **options):
        super().__init__("^", **options)

    def load_extensions(self):
        for extension in STARTUP_EXTENSIONS:
            try:
                self.load_extension(extension)
            except Exception as err:
                exc = '{}: {}'.format(type(err).__name__, err)
                logging.info('Failed to load extension {}\n{}'.format(extension, exc))

    @asyncio.coroutine
    async def logout(self):
        json_save(SAVE_FILE, ops=bot.extensions["AdminCommands"].ops, perms=bot.extensions["AdminCommands"].perms)
        await super().logout()

    @asyncio.coroutine
    async def save(self):
        json_save(SAVE_FILE, ops=bot.extensions["AdminCommands"].ops, perms=bot.extensions["AdminCommands"].perms)

    @asyncio.coroutine
    async def update_perms(self):
        bot.extensions["Commands"].perms.update(bot.extensions["AdminCommands"].perms)
        json_save(SAVE_FILE, ops=bot.extensions["AdminCommands"].ops, perms=bot.extensions["AdminCommands"].perms)

    @asyncio.coroutine
    async def on_ready(self):
        print('| Now logged in as')
        print('| {}'.format(self.user.name))
        print('| {}'.format(self.user.id))
        await bot.change_presence(game=discord.Game(name="Taking over the World", type=0))

    @asyncio.coroutine
    def on_command_error(self, ctx, exception):
        if type(exception) == discord.ext.commands.CommandNotFound:
            yield from ctx.send("Sorry, I don't understand \"{}\". May I suggest ^help?".format(ctx.invoked_with))
        elif type(exception) == discord.ext.commands.CheckFailure:
            logging.info("Woah, {} tried to run a command without permissions!".format(ctx.author))
        else:
            print('Ignoring exception in command {}'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)


def string_load(filename):
    out = []
    with open(filename, 'a+') as file:
        try:
            file.seek(0)
            out = file.readlines()
        except Exception as e:
            print(e)
    return out


def load_token():
    file = string_load(TOKEN_FILE)
    return file[0].strip()


def json_load(filename):
    with open(filename, 'a+') as file:
        try:
            file.seek(0)
            data = json.load(file)
        except json.JSONDecodeError as e:
            logging.warning(e)
            data = None
    return data


def build_trees(data):
    try:
        bot.extensions["AdminCommands"].ops.update(data['ops'])
        bot.extensions["AdminCommands"].perms.update(data['perms'])
        bot.extensions["Commands"].perms.update(data['perms'])
    except KeyError:
        logging.warning("Cog not loaded")


def json_save(filename, **options):
    with open(filename, 'w+') as file:
        try:
            out = dict()
            for key in options:
                out[key] = options[key]
            json.dump(out, file)
        except Exception as e:
            print(e)

if __name__ == "__main__":

    description = '''Greetings. I'm Talos, chat helper. My commands are:'''
    bot = Talos(description=description)
    bot.load_extensions()

    try:
        json_data = json_load(SAVE_FILE)
        if json_data is not None:
            build_trees(json_data)
        bot.run(load_token())
    finally:
        print("Talos Exiting")
