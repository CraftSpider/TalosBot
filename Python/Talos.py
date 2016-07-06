import discord
from discord.ext import commands
import random
import logging

#
#   Constants
#
VERSION = 2.0
BOOT_TIME = new Date()
ADMINS = ["Dino", "α|CraftSpider|Ω", "HiddenStorys"]
EGG_DEV = "wundrweapon"

#
#   Command Variables
#
NumWWs = 0
MaxWWs = 10
IsSleeping = 0



logging.basicConfig(level=logging.INFO)

description = '''Greetings. I'm Talos, chat helper. My commands are:'''
bot = commands.Bot(command_prefix='^', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def information():
    """Gives a short blurb about Talos."""
    await bot.say("Hello! I'm Talos, official PtP mod-bot.\nMy Developers are CraftSpider, Dino, and HiddenStorys.\nAny suggestions or bugs can be sent to my email, talos.ptp@gmail.com.")

@bot.command()
async def roll(dice : str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)

@bot.command(description='For when you wanna settle the score some other way')
async def choose(*choices : str):
    """Chooses between multiple choices."""
    await bot.say(random.choice(choices))

@bot.command()
async def joined(member : discord.Member):
    """Says when a member joined."""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))

@bot.group(pass_context=True)
async def cool(ctx):
    """Says if a user is cool.

    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await bot.say('No, {0.subcommand_passed} is not cool'.format(ctx))

@cool.command(name='Talos')
async def _bot():
    """Is the bot cool?"""
    await bot.say('Yes, Talos is cool.')

bot.run('MTk5OTY1NjEyNjkxMjkyMTYw.Cl2X_Q.SWyFAXsMeDG87vW6WERSLljDQIQ')
