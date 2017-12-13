"""
    Joke Commands cog for Talos
    Holds all Joke commands. Things that aren't necessarily useful, but are fun to play with.

    Author: CraftSpider
"""
import discord
import asyncio
import logging
from discord.ext import commands
from utils import fullwidth_transform

logging = logging.getLogger("talos.joke")


class JokeCommands:
    """These commands can be used by anyone, as long as Talos is awake.\nThey are really just for fun."""

    __slots__ = ['bot', 'database']

    def __init__(self, bot):
        """Initialize the JokeCommands cog. Takes in an instance of Talos to use while running."""
        self.bot = bot
        self.database = None
        if hasattr(bot, "database"):
            self.database = bot.database

    @commands.command(aliases=["Hi"], description="Say hello to Talos")
    async def hi(self, ctx, *, extra=""):
        """Talos is friendly, and love to say hello. Some rare people may invoke special responses."""
        if str(ctx.author) == "East#4048" and extra.startswith("there..."):
            async with ctx.typing():
                await asyncio.sleep(1)
                await ctx.send("Hello East.")
            await asyncio.sleep(1)
            async with ctx.typing():
                await asyncio.sleep(2)
                await ctx.send("Thank you. The same to you.")
            return
        await ctx.send("Hello there {}".format(ctx.author.name))

    @commands.command(description="Ask Talos for a favor, or have them ask others for one...")
    async def favor(self, ctx):
        """If East is in the same guild, Talos will ask them a favor... Otherwise, Talos isn't doing it"""
        east = ctx.guild.get_member(339119069066297355)
        if not east or east.status != discord.Status.online:
            await ctx.send("I'm afraid I can't do that, {}.".format(ctx.author.display_name))
            return
        await ctx.send("!East could I ask you for a favor? I need someone to verify my code.")
        await asyncio.sleep(2)
        async with ctx.typing():
            await asyncio.sleep(1)
            await ctx.send("Oh my. Well, if you insist ;)")

    @commands.command(description="Sometimes you just need it louder looking")
    async def aesthetic(self, ctx, *, text):
        """When you just need it in large, this is the command for you."""
        out = ""
        for char in text:
            out += fullwidth_transform.get(char, char)
        await ctx.send(out)


def setup(bot):
    bot.add_cog(JokeCommands(bot))
