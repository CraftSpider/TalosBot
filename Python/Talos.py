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
VERSION = "2.1.1"
BOOT_TIME = datetime.datetime.now()
EGG_DEV = "wundrweapon#4856"
STARTUP_EXTENSIONS = ["Commands", "UserCommands", "AdminCommands"]
SAVE_FILE = "./TalosData.dat"

#
#   Command Vars
#
is_sleeping = 0
perms = {}

# Replace this with your key before running Talos
STATIC_KEY = "MzMwMDYxOTk3ODQyNjI4NjIz.DFvCvw.w8azTi_Hf8wyB4LeaIVZqwXIln4"

# Initiate Logging
logging.basicConfig(level=logging.INFO)


# def handle_text():
#     while input() != "quit":
#         pass
#     print("quitting")
#     bot.stop()


class Talos(commands.Bot):

    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

    @asyncio.coroutine
    async def logout(self):
        save_file(SAVE_FILE, bot.extensions["AdminCommands"].ops, perms)
        await super().logout()

    @asyncio.coroutine
    async def save(self):
        save_file(SAVE_FILE, bot.extensions["AdminCommands"].ops, perms)

    @asyncio.coroutine
    async def on_ready(self):
        print('| Now logged in as')
        print('| ' + self.user.name)
        print('| ' + self.user.id)
        await bot.change_presence(game=discord.Game(name="Taking over the World", type="0"))

    @asyncio.coroutine
    def on_command_error(self, exception, context):
        if type(exception) == discord.ext.commands.CommandNotFound:
            yield from self.send_message(context.message.channel,
                                         "Sorry, I don't understand \"{}\". May I suggest ^help?"
                                         .format(context.invoked_with))
        print('Ignoring exception in command {}'.format(context.command), file=sys.stderr)
        traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)


def load_file(filename):
    with open(filename, 'a+') as file:
        try:
            file.seek(0)
            data = json.load(file)
        except json.JSONDecodeError as e:
            logging.warning(e)
            data = None
    return data


def build_trees(data):
    bot.extensions["AdminCommands"].ops.update(data['ops'])


def save_file(filename, ops, permissions):
    with open(filename, 'w+') as file:
        try:
            out = dict()
            out['ops'] = ops
            out['perms'] = permissions
            json.dump(out, file)
        except Exception as e:
            print(e)

if __name__ == "__main__":

    description = '''Greetings. I'm Talos, chat helper. My commands are:'''
    bot = Talos(command_prefix='^', description=description)

    for extension in STARTUP_EXTENSIONS:
        try:
            bot.load_extension(extension)
        except Exception as err:
            exc = '{}: {}'.format(type(err).__name__, err)
            logging.info('Failed to load extension {}\n{}'.format(extension, exc))
    # executor = ThreadPoolExecutor(2)
    # bot.future = asyncio.ensure_future(bot.loop.run_in_executor(executor, handle_text))
    try:
        json_data = load_file(SAVE_FILE)
        if json_data is not None:
            build_trees(json_data)
        bot.run(STATIC_KEY)
    finally:
        print("Talos Exiting")
