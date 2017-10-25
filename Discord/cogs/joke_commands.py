"""
    Joke Commands cog for Talos
    Holds all Joke commands. Things that aren't necessarily useful, but are fun to play with.

    Author: CraftSpider
"""
import discord
import asyncio
import logging
from discord.ext import commands

logging = logging.getLogger("talos.joke")


def perms_check():
    """Determine whether the person calling the command is an operator or admin."""

    def predicate(ctx):

        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            return True
        command = str(ctx.command)

        if not ctx.bot.get_guild_option(ctx.guild.id, "joke_commands"):
            return False
        perms = ctx.bot.get_perm_rules(ctx.guild.id, command)
        if len(perms) == 0:
            return True
        perms.sort(key=lambda x: x[3])
        for perm in perms:
            if perm[1] == "user" and perm[2] == str(ctx.author):
                return perm[4]
            elif perm[1] == "role":
                for role in ctx.author.roles:
                    if perm[2] == str(role):
                        return perm[4]
            elif perm[1] == "channel" and perm[2] == str(ctx.channel):
                return perm[4]
            elif perm[1] == "guild":
                return perm[4]
        return True

    return commands.check(predicate)


class JokeCommands:
    """These commands can be used by anyone, as long as Talos is awake.\nThey are really just for fun."""

    __slots__ = ['bot']

    def __init__(self, bot):
        """Initialize the JokeCommands cog. Takes in an instance of Talos to use while running."""
        self.bot = bot

    @commands.command(aliases=["Hi"])
    @perms_check()
    async def hi(self, ctx, *extra):
        """Say hi to Talos"""
        if str(ctx.author) == "East#4048" and extra[0] == "there...":
            async with ctx.typing():
                await asyncio.sleep(1)
                await ctx.send("Hello East.")
            await asyncio.sleep(1)
            async with ctx.typing():
                await asyncio.sleep(2)
                await ctx.send("Thank you. The same to you.")
            return
        await ctx.send("Hello there {}".format(ctx.author.name))

    @commands.command()
    @perms_check()
    async def favor(self, ctx):
        """If East is in the same server, ask them a favor..."""
        await ctx.send("!East could I ask you for a favor? I need someone to verify my code.")
        await asyncio.sleep(2)
        async with ctx.typing():
            await asyncio.sleep(1)
            await ctx.send("Oh my. Well, if you insist ;)")


def setup(bot):
    bot.add_cog(JokeCommands(bot))
