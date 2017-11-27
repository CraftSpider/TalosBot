"""
    Dev Commands cog for Talos.
    Holds all commands relevant to dev functions, things to alter all of Talos.

    Author: CraftSpider
"""

import discord
import logging
import re
import io
import utils
from datetime import datetime
from PIL import Image, ImageDraw
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
    """These commands can only be used by Talos Devs, and will work at any time. Several of them are very dangerous."""

    __slots__ = ['bot', 'database']

    def __init__(self, bot):
        """Initializes the AdminCommands cog. Takes an instance of Talos to use while running."""
        self.bot = bot
        self.database = None
        if hasattr(bot, "database"):
            self.database = bot.database

    @commands.command(hidden=True)
    @admin_check()
    async def playing(self, ctx, *, playing: str):
        """Changes the game Talos is playing"""
        await self.bot.change_presence(game=discord.Game(name=playing))
        await ctx.send("Now playing {}".format(playing))

    @commands.command(hidden=True)
    @admin_check()
    async def streaming(self, ctx, *, streaming: str):
        """Changes the game Talos is streaming"""
        await self.bot.change_presence(game=discord.Game(name=streaming, url="http://www.twitch.tv/talos_bot_", type=1))
        await ctx.send("Now streaming {}".format(streaming))

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
    async def grant_title(self, ctx, user: discord.User, *, title):
        profile = self.database.get_user(user.id)
        if not profile:
            raise utils.NotRegistered(user)
        if title == "None":
            title = None
        self.database.set_title(user.id, title)
        await ctx.send("Title `{}` granted to {}".format(title, str(user)))

    @commands.command(hidden=True)
    @admin_check()
    async def eval(self, ctx, *, program):
        """Evaluate a given string as python code. Prints the return, if not empty. This is not dangerous."""
        try:
            result = str(eval(program))
            if result is not None and result is not "":
                result = re.sub(r"([\\_*~])", r"\\\g<1>", result)
                await ctx.send("```py\n{}```".format(result))
        except Exception as e:
            await ctx.send("Program failed with {}: {}".format(e.__class__.__name__, e))

    @commands.command(hidden=True)
    @admin_check()
    async def exec(self, ctx, *, program):
        """Execute a given string as python code. replaces ';' with newlines and \t with tabs, for multiline."""\
            """ I laugh in the face of danger."""
        program = re.sub(r"(?<!\\)((?:\\\\)*);", "\n", program)
        program = re.sub(r"(?<!\\)\\((?:\\\\)*)t", "\t", program)
        try:
            exec(program)
        except Exception as e:
            await ctx.send("Program failed with {}: {}".format(e.__class__.__name__, e))

    @commands.command(hidden=True)
    @admin_check()
    async def sql(self, ctx, *, statement):
        """Execute arbitrary SQL code. Weeh, injection."""
        try:
            self.bot._cursor.execute(statement)
            await ctx.send(self.bot._cursor.fetchall())
        except Exception as e:
            await ctx.send("Statement failed with {}: {}".format(e.__class__.__name__, e))

    @commands.command(hidden=True)
    async def image(self, ctx, red=0, green=0, blue=0):
        start = datetime.now()
        image = Image.new("RGB", (250, 250), (red, green, blue))
        draw = ImageDraw.Draw(image)
        draw.rectangle([50, 50, 100, 100], fill=(red+50, green+50, blue+50))
        draw.rectangle([150, 50, 200, 100], fill=(red+50, green+50, blue+50))
        draw.rectangle([50, 175, 75, 200], fill=(red+50, green+50, blue+50))
        draw.rectangle([175, 175, 200, 200], fill=(red+50, green+50, blue+50))
        draw.rectangle([50, 200, 200, 225], fill=(red+50, green+50, blue+50))

        byteso = io.BytesIO()
        image.save(byteso, "png")
        byteso.seek(0)
        file = discord.File(byteso, filename="test.png")
        await ctx.send(file=file)
        end = datetime.now()
        await ctx.send(end - start)


def setup(bot):
    bot.add_cog(DevCommands(bot))
