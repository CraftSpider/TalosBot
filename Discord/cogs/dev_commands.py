"""
    Dev Commands cog for Talos.
    Holds all commands relevant to dev functions, things to alter all of Talos.

    Author: CraftSpider
"""

import discord
import logging
import re
from discord.ext import commands

# Configure Logging
log = logging.getLogger("talos.dev")


#
# Dev Command Check
#
def admin_check():
    """Determine whether the person calling the command is an admin."""
    def predicate(ctx):
        return ctx.author.id in ctx.bot.ADMINS
    return commands.check(predicate)


#
# Dev Cog Class
#
class DevCommands:

    __slots__ = ['bot']

    def __init__(self, bot):
        """Initializes the AdminCommands cog. Takes an instance of Talos to use while running."""
        self.bot = bot

    @commands.command(hidden=True)
    @admin_check()
    async def playing(self, ctx, *playing: str):
        """Changes the game Talos is playing"""
        game = " ".join(map(str, playing))
        await self.bot.change_presence(game=discord.Game(name=game))
        await ctx.send("Now playing {}".format(game))

    @commands.command(hidden=True)
    @admin_check()
    async def streaming(self, ctx, *streaming: str):
        """Changes the game Talos is streaming"""
        game = " ".join(map(str, streaming))
        await self.bot.change_presence(game=discord.Game(name=game, url="http://www.twitch.tv/CraftSpider", type=1))
        await ctx.send("Now streaming {}".format(game))

    @commands.command(hidden=True)
    @admin_check()
    async def stop(self, ctx):
        """Stops Talos running and logs it out."""
        await ctx.send("Et tū, Brute?")
        await self.bot.logout()

    @commands.command(hidden=True)
    @admin_check()
    async def verify(self, ctx):
        """Verifies Talos data, making sure that all existing guilds have proper data and non-existent guilds don't""" \
            """ have data."""
        added, removed = await self.bot.verify()
        await ctx.send("Data Verified. {} objects added, {} objects removed.".format(added, removed))

    @commands.command(hidden=True)
    @admin_check()
    async def master_nick(self, ctx, nick: str):
        """Changes Talos nickname in all servers"""
        for guild in self.bot.guilds:
            await guild.me.edit(nick=nick)
        await ctx.send("Nickname universally changed to {}".format(nick))

    @commands.command(hidden=True)
    @admin_check()
    async def eval(self, ctx, *text):
        """Evaluate a given string as python code. Prints the return, if not empty. This is not dangerous."""
        program = ' '.join(text)
        try:
            result = str(eval(program))
            if result is not None and result is not "":
                result = re.sub(r"([\\_*~])", r"\\\g<1>", result)
                await ctx.send(result)
        except Exception as e:
            await ctx.send("Program failed with {}: {}".format(e.__class__.__name__, e))

    @commands.command(hidden=True)
    @admin_check()
    async def exec(self, ctx, *text):
        """Execute a given string as python code. replaces ';' with newlines and \t with tabs, for multiline."""\
            """ I laugh in the face of danger."""
        program = ' '.join(text)
        program = re.sub(r"(?<!\\)((?:\\\\)*);", "\n", program)
        program = re.sub(r"(?<!\\)\\((?:\\\\)*)t", "\t", program)
        try:
            exec(program)
        except Exception as e:
            await ctx.send("Program failed with {}: {}".format(e.__class__.__name__, e))

    @commands.command(hidden=True)
    @admin_check()
    async def sql(self, ctx, *text):
        """Execute arbitrary SQL code. Weeh, injection."""
        statement = ' '.join(text)
        try:
            self.bot._cursor.execute(statement)
            await ctx.send(self.bot._cursor.fetchall())
        except Exception as e:
            await ctx.send("Statement failed with {}: {}".format(e.__class__.__name__, e))


def setup(bot):
    bot.add_cog(DevCommands(bot))
