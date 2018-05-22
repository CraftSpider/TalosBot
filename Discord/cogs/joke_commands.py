"""
    Joke Commands cog for Talos
    Holds all Joke commands. Things that aren't necessarily useful, but are fun to play with.

    Author: CraftSpider
"""
import discord
import asyncio
import logging
import utils
from discord.ext import commands

log = logging.getLogger("talos.joke")


class JokeCommands(utils.TalosCog):
    """These commands can be used by anyone, as long as Talos is awake.\nThey are really just for fun."""

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
            out += utils.fullwidth_transform.get(char, char)
        await ctx.send(out)

    @commands.command(description="Feed your cat addiction")
    async def catpic(self, ctx):
        """Returns a random cat picture. Sourced from The Cap API."""
        file = await self.bot.session.get_cat_pic()
        await ctx.send(file=file)

    @commands.command(description="There's a relevant XKCD for everything")
    async def xkcd(self, ctx, comic: int=0):
        """Gets an XKCD comic with the given number, or the current one if one isn't specified, and displays it."""
        if comic < 0:
            await ctx.send("Requested XKCD can't be negative")
            return
        data = await self.bot.session.get_xkcd(comic or None)
        title = data["title"]
        img_data = data["img_data"]
        img = data["img"]
        alt = data["alt"]
        print(img)
        if ctx.bot.should_embed(ctx):
            with utils.PaginatedEmbed() as embed:
                embed.title = title
                embed.set_image(url=img)
                embed.set_footer(text=alt)
            await ctx.send(embed=embed)
        else:
            await ctx.send("**" + title + "**\n" + alt, file=img_data)


def setup(bot):
    bot.add_cog(JokeCommands(bot))
