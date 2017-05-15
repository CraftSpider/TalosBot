import discord
from discord.ext import commands
import random
import logging
import datetime
import time

#
#   Constants
#
VERSION = 2.0
BOOT_TIME = datetime.datetime.now()
ADMINS = ["Dino", "α|CraftSpider|Ω", "HiddenStorys"]
EGG_DEV = "wundrweapon"
STATIC_KEY = "MTk5OTY1NjEyNjkxMjkyMTYw.C9kj5g.zx63pLGVm7oJ_YOod1L2HLurm2g" #Replace this with your key before running Talos

#
#   Command Variables
#
num_wws = 0
max_wws = 10
is_sleeping = 0

#
#   Generator Strings
#
noun = ["dog", "cat", "robot", "astronaut", "man", "woman", "person", "child", "giant", "elephant", "zebra", "animal", "box", "tree", "wizard", "mage", "swordsman", "soldier", "inventor", "doctor", "Talos", "dinosaur", "insect", "nerd", "dancer", "singer", "actor", "barista", "acrobat", "gamer", "writer", "dragon"]
adjective = ["happy", "sad", "athletic", "giant", "tiny", "smart", "silly", "unintelligent", "funny", "coffee-loving", "lazy", "spray-tanned", "angry", "disheveled", "annoying", "loud", "quiet", "shy", "extroverted", "jumpy", "ditzy", "strong", "weak", "smiley", "annoyed", "dextrous"]
goal = ["fly around the world", "go on a date", "win a race", "tell their crush how they feel", "find their soulmate", "write a chatbot", "get into university", "graduate high school", "plant a hundred trees", "find their biological parents", "fill their bucket list", "find atlantis", "learn magic", "learn to paint", "drive a car", "pilot a spaceship", "leave Earth", "go home", "redo elementary school", "not spill their beer"]
obstacle = ["learning to read", "fighting aliens", "saving the world", "doing algebra", "losing their hearing", "losing their sense of sight", "learning the language", "hacking the mainframe", "coming of age", "the nuclear apocalypse is happening", "incredibly drunk", "drinking coffee", "surfing", "spying on the bad guys", "smelling terrible", "having a bad hair day", "exploring the new planet", "on the moon", "on Mars"]

place = ["pub", "spaceship", "museum", "office", "jungle", "forest", "coffee shop", "store", "market", "station", "tree", "hut", "house", "bed", "bus", "car", "dormitory", "school", "desert", "ballroom", "cattery", "shelter", "street"]
place_adjective = ["quiet", "loud", "crowded", "deserted", "bookish", "colorful", "balloon-filled", "book", "tree", "money", "video game", "cat", "dog", "busy", "apocalypse", "writer", "magic", "light", "dark", "robotic", "futuristic", "old-timey"]
action = ["learn to read", "jump up and down", "cry a lot", "cry a little", "smile", "spin in a circle", "get arrested", "dance to the music", "listen to your favourite song", "eat all the food", "win the lottery", "hack the mainframe", "save the world", "find atlantis", "get accepted to Hogwarts", "swim around", "defy gravity", "spy on the bad guys", "drive a car", "enter the rocket ship", "learn math", "write a lot", "do gymnastics"]

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
async def choose(*input : str):
    """Chooses between multiple choices."""
    result =  " ".join(input)
    await bot.say("I'm choosing between: " + result + ".")
    choices = result.split(", ")
    
    await bot.say(random.choice(choices))

@bot.command()
async def wordwar(length : str): #Need to find way to wait without blocking threads. Command currently nonoperational
    """Runs an X minute long word-war"""
    try:
        length = int(length)
    except length > 60 or length < 1:
        await bot.say("Please choose a length between 1 and 60 minutes.")
        return
    except Exception:
        await bot.say("Please specify the length of your word war (in minutes).")
        return
    
    await bot.say("Word War for " + str(length) + " minutes.")
    await bot.say("Word War Over")
    

@bot.command()
async def joined(member : discord.Member):
    """Says when a member joined."""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))

@bot.group(pass_context=True)
async def generate(ctx):
    """Generates a crawl or prompt"""
    if ctx.invoked_subcommand is None:
        await bot.say("Valid options are 'prompt' and 'crawl'.")

@generate.command(name='crawl')
async def _crawl():
    """Generates a crawl"""
    await bot.say("You enter the " + random.choice(place_adjective) + " " + random.choice(place) + ". Write " + str(random.randint(50, 500)) + " words as you " + random.choice(action) + ".")

@generate.command(name='prompt')
async def _prompt():
    """Generates a prompt"""
    await bot.say("A story about a " + random.choice(adjective) + " " + random.choice(noun) + " who must " + random.choice(goal) + " while " + random.choice(obstacle) + ".")

bot.run(STATIC_KEY)
