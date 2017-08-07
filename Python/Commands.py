import discord
from discord.ext import commands
import asyncio
import random
import datetime
from collections import defaultdict

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Python import Talos

active_pw = defaultdict(lambda: None)


def sort_mem(member):
    return member.end - member.start


class Commands:
    """These commands can be used by anyone, as long as Talos is awake.\nThey don't care who is using them."""
    def __init__(self, bot):
        self.bot = bot
    
    #
    #   Generator Strings
    #
    noun = ["dog", "cat", "robot", "astronaut", "man", "woman", "person", "child", "giant", "elephant", "zebra",
            "animal", "box", "tree", "wizard", "mage", "swordsman", "soldier", "inventor", "doctor", "Talos",
            "dinosaur", "insect", "nerd", "dancer", "singer", "actor", "barista", "acrobat", "gamer", "writer",
            "dragon"]
    adjective = ["happy", "sad", "athletic", "giant", "tiny", "smart", "silly", "unintelligent", "funny",
                 "coffee-loving", "lazy", "spray-tanned", "angry", "disheveled", "annoying", "loud", "quiet", "shy",
                 "extroverted", "jumpy", "ditzy", "strong", "weak", "smiley", "annoyed", "dextrous"]
    goal = ["fly around the world", "go on a date", "win a race", "tell their crush how they feel",
            "find their soulmate", "write a chatbot", "get into university", "graduate high school",
            "plant a hundred trees", "find their biological parents", "fill their bucket list", "find atlantis",
            "learn magic", "learn to paint", "drive a car", "pilot a spaceship", "leave Earth", "go home",
            "redo elementary school", "not spill their beer"]
    obstacle = ["learning to read", "fighting aliens", "saving the world", "doing algebra", "losing their hearing",
                "losing their sense of sight", "learning the language", "hacking the mainframe", "coming of age",
                "the nuclear apocalypse is happening", "incredibly drunk", "drinking coffee", "surfing",
                "spying on the bad guys", "smelling terrible", "having a bad hair day", "exploring the new planet",
                "on the moon", "on Mars"]
    
    place = ["pub", "spaceship", "museum", "office", "jungle", "forest", "coffee shop", "store", "market", "station",
             "tree", "hut", "house", "bed", "bus", "car", "dormitory", "school", "desert", "ballroom", "cattery",
             "shelter", "street"]
    place_adjective = ["quiet", "loud", "crowded", "deserted", "bookish", "colorful", "balloon-filled", "book", "tree",
                       "money", "video game", "cat", "dog", "busy", "apocalypse", "writer", "magic", "light", "dark",
                       "robotic", "futuristic", "old-timey"]
    action = ["learn to read", "jump up and down", "cry a lot", "cry a little", "smile", "spin in a circle",
              "get arrested", "dance to the music", "listen to your favourite song", "eat all the food",
              "win the lottery", "hack the mainframe", "save the world", "find atlantis", "get accepted to Hogwarts",
              "swim around", "defy gravity", "spy on the bad guys", "drive a car", "enter the rocket ship",
              "learn math", "write a lot", "do gymnastics"]
    
    #
    #   User Commands
    #
    
    @commands.command()
    async def information(self):
        """Gives a short blurb about Talos."""
        await self.bot.say("Hello! I'm Talos, official PtP mod-bot.\
                           \nMy Developers are CraftSpider, Dino, and HiddenStorys.\
                           \nAny suggestions or bugs can be sent to my email, talos.ptp@gmail.com.")

    @commands.command()
    async def version(self):
        """Returns Talos version."""
        await self.bot.say("Version: {0}".format(Talos.VERSION))

    @commands.command()
    async def roll(self, dice: str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await self.bot.say('Format has to be in NdN!')
            return
    
        result = ', '.join(str(random.randint(1, limit)) for _ in range(rolls))
        await self.bot.say(result)
        
    @commands.command(description='For when you wanna settle the score some other way')
    async def choose(self, *choices: str):
        """Chooses between multiple choices."""
        await self.bot.say("I'm choosing between: " + ", ".join(choices) + ".")
        await self.bot.say(random.choice(choices).strip())

    @commands.command()
    async def time(self):
        """Prints out the current time in UTC, HH:MM:SS format"""
        await self.bot.say("It's time to get a watch. {0}".format(datetime.datetime.utcnow().strftime("%H:%M:%S")))
    
    @commands.command(aliases=["ww", "WW"])
    async def wordwar(self, length: str="", start: str=""):
        """Runs an X minute long word-war"""
        try:
            length = float(length)
        except Exception:
            await self.bot.say("Please specify the length of your word war (in minutes).")
            return
        if length > 60 or length < 1:
            await self.bot.say("Please choose a length between 1 and 60 minutes.")
            return

        if start:
            try:
                if start[0] == ":":
                    start = int(start[1:])
                elif start[0].isnumeric():
                    start = int(start)
                else:
                    raise Exception
            except Exception:
                await self.bot.say("Start time format broken. Starting now.")
                start = ""
            if start != "" and (start > 59 or start < 0):
                await self.bot.say("Please specify a start time in the range of 0 to 59.")
                return

        if start:
            dif = abs(datetime.datetime.utcnow() - datetime.datetime.utcnow().replace(minute=start, second=0))
            await self.bot.say("Starting WW at :{0:02}".format(start))
            await asyncio.sleep(dif.total_seconds())
        minutes = "minutes" if length != 1 else "minute"
        await self.bot.say("Word War for {0:g} {1}.".format(length, minutes))
        await asyncio.sleep(length * 60)
        await self.bot.say("Word War Over")

    @commands.command()
    async def credits(self):
        """Giving credit where it is due"""
        await self.bot.say("Primary Developers: CraftSpider, Dino.\nOther contributors: Wundrweapon, HiddenStorys")
    
    @commands.command()
    async def joined(self, member: discord.Member):
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
        await self.bot.say("You enter the " + random.choice(self.place_adjective) + " " + random.choice(self.place) +
                           ". Write " + str(random.randint(50, 500)) + " words as you " + random.choice(self.action) +
                           ".")
    
    @generate.command(name='prompt')
    async def _prompt(self):
        """Generates a prompt"""
        await self.bot.say("A story about a " + random.choice(self.adjective) + " " + random.choice(self.noun) +
                           " who must " + random.choice(self.goal) + " while " + random.choice(self.obstacle) + ".")

    @commands.group(pass_context=True, aliases=["pw", "PW"])
    async def productivitywar(self, ctx):
        """Commands for a productivity war."""
        if ctx.invoked_subcommand is None:
            await self.bot.say("Valid options are 'create', 'join', 'start', 'leave', and 'end'.")

    @productivitywar.command(name='create', pass_context=True)
    async def _create(self, ctx):
        """Begins a new PW, if one isn't already running."""
        if active_pw[ctx.message.server.id] is not None:
            await self.bot.say("There's already a PW going on. Would you like to **join**?")
        else:
            await self.bot.say("Creating a new PW.")
            active_pw[ctx.message.server.id] = PW()
            active_pw[ctx.message.server.id].join(ctx.message.author)

    @productivitywar.command(name='join', pass_context=True)
    async def _join(self, ctx):
        """Join a currently running PW, if you aren't already in it."""
        if active_pw[ctx.message.server.id] is not None:
            if active_pw[ctx.message.server.id].join(ctx.message.author):
                await self.bot.say("User {0} joined the PW.".format(ctx.message.author))
            else:
                await self.bot.say("You're already in this PW.")
        else:
            await self.bot.say("No PW to join. Maybe you want to **create** one?")

    @productivitywar.command(name='start', pass_context=True)
    async def _start(self, ctx):
        """Start a PW that isn't yet begun."""
        if active_pw[ctx.message.server.id] is not None:
            if not active_pw[ctx.message.server.id].get_started():
                await self.bot.say("Starting PW")
                active_pw[ctx.message.server.id].begin()
            else:
                await self.bot.say("PW has already started! Would you like to **join**?")
        else:
            await self.bot.say("No PW to start. Maybe you want to **create** one?")

    @productivitywar.command(name='leave', pass_context=True)
    async def _leave(self, ctx):
        """End your involvement in a PW, if you're the last person, the whole thing ends."""
        if active_pw[ctx.message.server.id] is not None:
            leave = active_pw[ctx.message.server.id].leave(ctx.message.author)
            if leave == 0:
                await self.bot.say("User {0} left the PW.".format(ctx.message.author))
            elif leave == 1:
                await self.bot.say("You aren't in the PW! Would you like to **join**?")
            elif leave == 2:
                await self.bot.say("You've already left this PW! Are you going to **end** it?")
            if active_pw[ctx.message.server.id].get_finished():
                await self._end.invoke(ctx)
        else:
            await self.bot.say("No PW to start. Maybe you want to **create** one?")

    @productivitywar.command(name='end', pass_context=True)
    async def _end(self, ctx):
        """End the whole PW, if one is currently running."""
        if active_pw[ctx.message.server.id] is None:
            await self.bot.say("There's currently no PW going on. Would you like to **create** one?")
        elif not active_pw[ctx.message.server.id].get_started():
            await self.bot.say("Deleting un-started PW.")
            active_pw[ctx.message.server.id] = None
        else:
            await self.bot.say("Ending PW.")
            active_pw[ctx.message.server.id].finish()
            cur_pw = active_pw[ctx.message.server.id]
            out = "```"
            out += "Start: {0}\n".format(cur_pw.start.replace(microsecond=0).strftime("%b %d - %H:%M:%S"))
            out += "End: {0}\n".format(cur_pw.end.replace(microsecond=0).strftime("%b %d - %H:%M:%S"))
            out += "Total: {0}\n".format(cur_pw.end.replace(microsecond=0) - cur_pw.start.replace(microsecond=0))
            out += "Times:\n"
            cur_pw.members.sort(key=sort_mem, reverse=True)
            for member in cur_pw.members:
                out += "    {0} - {1}\n".format(member.user, member.end.replace(microsecond=0) - member.start.replace(microsecond=0))
            out += "```"
            await self.bot.say(out)
            active_pw[ctx.message.server.id] = None

    @productivitywar.command(name='dump', pass_context=True, hidden=True)
    async def _dump(self, ctx):
        """Dumps info about the current state of a running PW"""
        cur_pw = active_pw[ctx.message.server.id]
        if cur_pw is None:
            await self.bot.say("No PW currently running")
            return
        out = "```"
        out += "Start: {0}\n".format(cur_pw.start)
        out += "End: {0}\n".format(cur_pw.end)
        out += "Members:\n"
        for member in cur_pw.members:
            out += "    {0} - {1} - {2}\n".format(member, member.start, member.end)
        out += "```"
        await self.bot.say(out)


class PW:

    def __init__(self):
        self.start = None
        self.end = None
        self.members = []

    def get_started(self):
        return self.start is not None

    def get_finished(self):
        return self.end is not None

    def begin(self):
        self.start = datetime.datetime.utcnow()
        for member in self.members:
            if not member.get_started():
                member.begin(self.start)

    def finish(self):
        self.end = datetime.datetime.utcnow()
        for member in self.members:
            if not member.get_finished():
                member.finish(self.end)

    def join(self, member):
        if PW_Member(member) not in self.members:
            new_mem = PW_Member(member)
            if self.get_started():
                new_mem.begin(datetime.datetime.utcnow())
            self.members.append(new_mem)
            return True
        else:
            return False

    def leave(self, member):
        if PW_Member(member) in self.members:
            for user in self.members:
                if user == PW_Member(member):
                    if user.get_finished():
                        return 2
                    else:
                        user.finish(datetime.datetime.utcnow())
            for user in self.members:
                if not user.get_finished():
                    return 0
            self.finish()
            return 0
        else:
            return 1


class PW_Member:

    def __init__(self, user):
        self.user = user
        self.start = None
        self.end = None

    def __str__(self):
        return str(self.user)

    def __eq__(self, other):
        return isinstance(other, PW_Member) and self.user == other.user

    def get_len(self):
        if self.end is None:
            return -1
        else:
            return self.start - self.end

    def get_started(self):
        return self.start is not None

    def get_finished(self):
        return self.end is not None

    def begin(self, time):
        self.start = time

    def finish(self, time):
        self.end = time


def setup(bot):
    bot.add_cog(Commands(bot))
