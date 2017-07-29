import discord
from discord.ext import commands
import logging
import datetime


startup_extensions = ["Commands", "UserCommands", "AdminCommands"]

#
#   Constants
#
VERSION = 2.0
BOOT_TIME = datetime.datetime.now()
ADMINS = ["Dino", "α|CraftSpider|Ω", "HiddenStorys"]
EGG_DEV = "wundrweapon"
STATIC_KEY = "MzMwMDYxOTk3ODQyNjI4NjIz.DFvCvw.w8azTi_Hf8wyB4LeaIVZqwXIln4" #Replace this with your key before running Talos

#
#   Command Variables
#
num_wws = 0
max_wws = 10
is_sleeping = 0

logging.basicConfig(level=logging.INFO)

description = '''Greetings. I'm Talos, chat helper. My commands are:'''
bot = commands.Bot(command_prefix='^', description=description)

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
    bot.run(STATIC_KEY)
