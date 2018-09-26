"""
    Joke Commands cog for Talos
    Holds all Joke commands. Things that aren't necessarily useful, but are fun to play with.

    Author: CraftSpider
"""
import typing
import datetime as dt
import discord
import asyncio
import logging
import utils
from discord.ext import commands

log = logging.getLogger("talos.joke")


class JokeCommands(utils.TalosCog):
    """These commands are really just for fun. Some of them may not have an obvious purpose, make of them as you"""\
        """ will."""

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
        stream, filename = await self.bot.session.get_cat_pic()
        file = discord.File(stream, filename=filename)
        await ctx.send(file=file)

    @commands.command(description="Ask Talos for a favor, or have them ask others for one...")
    async def favor(self, ctx):
        """If East is in the same guild, Talos will ask them a favor... Otherwise, Talos isn't doing it"""
        east = ctx.guild.get_member(339119069066297355)
        if not east or east.status != discord.Status.online:
            await ctx.send(f"I'm afraid I can't do that, {ctx.author.display_name}.")
            return
        await ctx.send("!East could I ask you for a favor? I need someone to verify my code.")
        await asyncio.sleep(2)
        async with ctx.typing():
            await asyncio.sleep(1)
            await ctx.send("Oh my. Well, if you insist ;)")

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
        await ctx.send(f"Hello there {ctx.author.name}")

    @commands.command(description="There's a relevant XKCD for everything")
    async def xkcd(self, ctx, comic: int=0):
        """Gets an XKCD comic with the given number, or the current one if one isn't specified, and displays it."""
        if comic < 0:
            await ctx.send("Requested XKCD can't be negative")
            return
        data = await self.bot.session.get_xkcd(comic or None)
        title = data["title"]
        img_data = discord.File(data["img_data"])
        img = data["img"]
        alt = data["alt"]
        if self.bot.should_embed(ctx):
            with utils.PaginatedEmbed() as embed:
                embed.title = title
                embed.set_image(url=img)
                embed.set_footer(text=alt)
                embed.timestamp = dt.datetime(year=int(data["year"]), month=int(data["month"]), day=int(data["day"]))
            await ctx.send(embed=embed)
        else:
            await ctx.send("**" + title + "**\n" + alt, file=img_data)

    @commands.command(description="SMBC: XKCD but philosophy and butt jokes")
    async def smbc(self, ctx, comic: typing.Union[utils.DateConverter["%Y-%m-%d"], int, str] = None):
        """Gets an SMBC from a given date, number, or id. Or, if not specified, it gets the most recent one. """\
            """Necessarily slightly slow due to technical limitations"""
        if isinstance(comic, int) and comic <= 0:
            await ctx.send("Comic number should be greater than 0")
        if comic is None:
            comic = 0
        comic_list = await self.bot.session.get_smbc_list()
        if isinstance(comic, (dt.date, dt.datetime)):
            strf = comic.strftime("%Y-%m-%d")
            for el in comic_list:
                if el.get_attribute("value") == strf:
                    comic_id = comic
                    break
            else:
                await ctx.send(f"No comic for date {comic} found")
                return
        elif isinstance(comic, int):
            comic_id = comic_list[comic - 1].get_attribute("value")
        else:
            for el in comic_list:
                if el.get_attribute("value") == comic:
                    comic_id = comic
                    break
            else:
                await ctx.send(f"No comic with id {comic} found")
                return

        data = await self.bot.session.get_smbc(comic_id)

        if self.bot.should_embed(ctx):
            with utils.PaginatedEmbed() as embed:
                embed.title = data["title"]
                embed.set_image(url=data["img"])
                embed.set_footer(text=data["alt"])
                embed.timestamp = data["time"]
            await ctx.send(embed=embed)
        else:
            await ctx.send("**" + data["title"] + "**\n" + data["alt"], file=discord.File(data["img_data"]))


def setup(bot):
    bot.add_cog(JokeCommands(bot))
