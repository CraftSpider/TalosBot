import discord
from discord.ext import commands
import time
import asyncio
import random


class Commands:
    """These commands can be used by anyone, as long as Talos is awake.\nThey don't care who is using them."""
    def __init__(self, bot):
        self.bot = bot
    
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
    
    #
    #   User Commands
    #
    
    @commands.command()
    async def information(self):
        """Gives a short blurb about Talos."""
        await self.bot.say("Hello! I'm Talos, official PtP mod-bot.\nMy Developers are CraftSpider, Dino, and HiddenStorys.\nAny suggestions or bugs can be sent to my email, talos.ptp@gmail.com.")

    @commands.command()
    async def roll(self, dice : str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await self.bot.say('Format has to be in NdN!')
            return
    
        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await self.bot.say(result)
        
    @commands.command(description='For when you wanna settle the score some other way')
    async def choose(self, *input : str):
        """Chooses between multiple choices."""
        logging.info(input)
        await self.bot.say("I'm choosing between: " + ", ".join(input) + ".")
        await self.bot.say(random.choice(input).strip())
    
    @commands.command()
    async def wordwar(self, length : str):
        """Runs an X minute long word-war"""
        try:
            length = float(length)
        except length > 60 or length < 1:
            await self.bot.say("Please choose a length between 1 and 60 minutes.")
            return
        except Exception:
            await self.bot.say("Please specify the length of your word war (in minutes).")
            return
            
        await self.bot.say("Word War for " + str(length) + " minutes.")
        await asyncio.sleep(length * 60)
        await self.bot.say("Word War Over")
        
    @commands.command()
    async def credits(self):
        """Giving credit where it is due"""
        await self.bot.say("Primary Developers: CraftSpider, Dino.\nOther contributors: Wundrweapon, HiddenStorys")
    
    @commands.command()
    async def joined(self, member : discord.Member):
        """Says when a member joined."""
        await self.bot.say('{0.name} joined in {0.joined_at}'.format(member))
    
    @commands.command()
    async def uptime(self):
        """To figure out how long the bot has been online."""
        pass
    
    @commands.group(pass_context=True)
    async def generate(self, ctx):
        """Generates a crawl or prompt"""
        if ctx.invoked_subcommand is None:
            await self.bot.say("Valid options are 'prompt' and 'crawl'.")
    
    @generate.command(name='crawl')
    async def _crawl(self):
        """Generates a crawl"""
        await self.bot.say("You enter the " + random.choice(place_adjective) + " " + random.choice(place) + ". Write " + str(random.randint(50, 500)) + " words as you " + random.choice(action) + ".")
    
    @generate.command(name='prompt')
    async def _prompt(self):
        """Generates a prompt"""
        await self.bot.say("A story about a " + random.choice(adjective) + " " + random.choice(noun) + " who must " + random.choice(goal) + " while " + random.choice(obstacle) + ".")


def setup(bot):
    bot.add_cog(Commands(bot))
