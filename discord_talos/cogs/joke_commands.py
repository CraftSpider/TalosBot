"""
    Joke Commands cog for Talos
    Holds all Joke commands. Things that aren't necessarily useful, but are fun to play with.

    Author: CraftSpider
"""
import typing
import datetime as dt
import discord
import discord.ext.commands as commands
import asyncio
import logging
import random
import utils
import utils.dutils as dutils

log = logging.getLogger("talos.joke")


class JokeCommands(dutils.TalosCog):
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
        data = await self.bot.session.get_cat_pic()
        file = discord.File(data["img_data"], filename=data["filename"])
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
        if data is None:
            await ctx.send(f"No comic for ID `{comic}` found")
            return
        title = data["title"]
        img = data["img"]
        alt = data["alt"]
        if self.bot.should_embed(ctx):
            with dutils.PaginatedEmbed() as embed:
                embed.title = title
                embed.set_image(url=img)
                embed.set_footer(text=alt)
                embed.timestamp = dt.datetime(year=int(data["year"]), month=int(data["month"]), day=int(data["day"]))
            await ctx.send(embed=embed)
        else:
            img_data = discord.File(data["img_data"], filename=data["filename"])
            await ctx.send("**" + title + "**\n" + alt, file=img_data)

    @commands.command(description="SMBC: XKCD but philosophy and butt jokes")
    async def smbc(self, ctx, comic: typing.Union[dutils.DateConverter["%Y-%m-%d"], int, str] = None):
        """Gets an SMBC from a given date, number, or id. Or, if not specified, it gets the most recent one. """\
            """Necessarily slightly slow to search by date due to technical limitations"""
        if isinstance(comic, int) and comic <= 0:
            await ctx.send("Comic number should be greater than 0")
        if comic is None:
            comic = 0

        if isinstance(comic, (dt.date, dt.datetime)):
            comic_list = await self.bot.session.get_smbc_list()
            strf = comic.strftime("%Y-%m-%d")
            for el in comic_list:
                time = dt.datetime.strptime(el.innertext.split("-")[0].strip(), "%B %d, %Y").strftime("%Y-%m-%d")
                if time == strf:
                    comic_id = comic
                    break
            else:
                await ctx.send(f"No comic for date `{comic}` found")
                return
        else:
            comic_id = comic

        data = await self.bot.session.get_smbc(comic_id)

        if data is None:
            await ctx.send(f"No comic with ID `{comic}` found")
            return

        if self.bot.should_embed(ctx):
            with dutils.PaginatedEmbed() as embed:
                embed.title = data["title"]
                embed.set_image(url=data["img"])
                embed.set_footer(text=data["alt"])
                embed.timestamp = data["time"]
            await ctx.send(embed=embed)
        else:
            await ctx.send("**" + data["title"] + "**\n" + data["alt"],
                           file=discord.File(data["img_data"], filename=data["filename"]))

    @commands.command(description="Display a random message", hidden=True)
    async def roulette(self, ctx):
        """Picks between a couple random message options and posts it. Here because wundr bugged me till I added it"""
        choices = ["This is the end of the world", "And I don't know what to put here"]
        await ctx.send(random.choice(choices))


def setup(bot):
    """
        Sets up the JokeCommands extension. Adds the JokeCommands cog to the bot
    :param bot: Bot this extension is being setup for
    """
    bot.add_cog(JokeCommands(bot))
