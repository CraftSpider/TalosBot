import discord
from discord.ext import commands
import logging
import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor


startup_extensions = ["Commands", "UserCommands", "AdminCommands"]

#
#   Constants
#
VERSION = 2.0
BOOT_TIME = datetime.datetime.now()
EGG_DEV = "wundrweapon"
# Replace this with your key before running Talos
STATIC_KEY = "MzMwMDYxOTk3ODQyNjI4NjIz.DFvCvw.w8azTi_Hf8wyB4LeaIVZqwXIln4"

#
#   Command Variables
#
num_wws = 0
max_wws = 10
is_sleeping = 0

logging.basicConfig(level=logging.INFO)


def handle_text():
    while input() != "quit":
        pass
    bot.stop()


class Talos(commands.Bot):

    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

    def stop(self):
        try:
            self.loop.run_until_complete(self.logout())
        except Exception as e:
            pass


description = '''Greetings. I'm Talos, chat helper. My commands are:'''
bot = Talos(command_prefix='^', description=description)


@bot.event
async def on_ready():
    print('| Now logged in as')
    print('| ' + bot.user.name)
    print('| ' + bot.user.id)
    await bot.change_presence(game=discord.Game(name="Taking over the World", type="0"))


if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            logging.info('Failed to load extension {}\n{}'.format(extension, exc))
    executor = ThreadPoolExecutor(2)
    asyncio.ensure_future(bot.loop.run_in_executor(executor, handle_text))
    try:
        bot.run(STATIC_KEY)
    finally:
        print("Talos Exiting")