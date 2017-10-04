"""
    Joke Commands cog for Talos
    Holds all Joke commands. Things that aren't necessarily useful, but are fun to play with.

    Author: CraftSpider
"""
import discord
import asyncio
from discord.ext import commands

# Ops list. Filled on bot load, altered through the add and remove op commands.
ops = {}
# Permissions list. Filled on bot load, altered by command
perms = {}
# Options list. Filled on bot load, altered by command.
options = {}


def perms_check():
    """Determine whether the person calling the command is an operator or admin."""

    def predicate(ctx):

        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            return True
        guild_id = str(ctx.guild.id)
        command = str(ctx.command)

        if not options[guild_id]["JokeCommands"]:
            return False
        if command not in perms[guild_id].keys():
            return True
        if "user" in perms[guild_id][command].keys():
            for key in perms[guild_id][command]["user"].keys():
                if key == str(ctx.author):
                    return perms[guild_id][command]["user"][key]
        if "role" in perms[guild_id][command].keys():
            for key in perms[guild_id][command]["role"].keys():
                for role in ctx.author.roles:
                    if key == str(role):
                        return perms[guild_id][command]["role"][key]
        if "channel" in perms[guild_id][command].keys():
            for key in perms[guild_id][command]["channel"].keys():
                if key == str(ctx.channel):
                    return perms[guild_id][command]["channel"][key]
        if "guild" in perms[guild_id][command].keys():
            return perms[guild_id][command]["guild"]
        return True

    return commands.check(predicate)


class JokeCommands:
    """These commands can be used by anyone, as long as Talos is awake.\nThey are really just for fun."""

    __slots__ = ['bot']

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="Hi")
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
