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
import asyncio
from datetime import datetime
from PIL import Image, ImageDraw
from discord.ext import commands

# Configure Logging
log = logging.getLogger("talos.dev")


#
# Dev Command Check
#
def dev_check(self, ctx):
    """Determine whether the person calling the command is an admin."""
    return ctx.author.id in ctx.bot.ADMINS


#
# Dev Cog Class
#
class DevCommands(utils.TalosCog):
    """These commands can only be used by Talos Devs, and will work at any time. Several of them are very """\
        """dangerous. Also, they are all hidden from the help command, thus why there's no list here."""

    __local_check = dev_check

    @commands.command(hidden=True, description="Change what Talos is playing")
    async def playing(self, ctx, *, playing: str):
        """Changes what Talos is playing, the thing displayed under the name in the user list."""
        await self.bot.change_presence(game=discord.Game(name=playing))
        await ctx.send("Now playing {}".format(playing))

    @commands.command(hidden=True, description="Change what Talos is streaming")
    async def streaming(self, ctx, *, streaming: str):
        """Changes what Talos is streaming, the thing displayed under the name in the user list."""
        await self.bot.change_presence(game=discord.Game(name=streaming, url="http://www.twitch.tv/talos_bot_", type=1))
        await ctx.send("Now streaming {}".format(streaming))

    @commands.command(hidden=True, description="Change what Talos is listening to")
    async def listening(self, ctx, *, listening: str):
        """Changes what Talos is listening to, the thing displayed under the name in the user list."""
        await self.bot.change_presence(game=discord.Game(name=listening, type=2))
        await ctx.send("Now listening to {}".format(listening))

    @commands.command(hidden=True, description="Change what Talos is watching")
    async def watching(self, ctx, *, watching: str):
        """Changes what Talos is watching, the thing displayed under the name in the user list."""
        await self.bot.change_presence(game=discord.Game(name=watching, type=3))
        await ctx.send("Now watching {}".format(watching))

    @commands.command(hidden=True, description="Kills Talos process")
    async def stop(self, ctx):
        """Stops Talos running and logs it out safely, killing the Talos process."""
        await ctx.send("Et tū, Brute?")
        await self.bot.logout()

    @commands.command(hidden=True, description="Change Talos' nickname everywhere")
    async def master_nick(self, ctx, nick: str):
        """Sets Talos' nickname in all guilds it is in."""
        for guild in self.bot.guilds:
            await guild.me.edit(nick=nick)
        await ctx.send("Nickname universally changed to {}".format(nick))

    @commands.command(hidden=True, description="List various IDs")
    async def idlist(self, ctx):
        """Lists off IDs of things that are a pain to get IDs from. Currently Roles and Channels."""
        out = "```\n"
        out += "Roles:\n"
        for role in ctx.guild.roles:
            out += "  {}: {}\n".format(role.name, role.id).replace("@everyone", "@\u200beveryone")
        out += "Channels:\n"
        for channel in ctx.guild.channels:
            out += "  {}: {}\n".format(channel.name, channel.id)
        out += "```"
        await ctx.send(out)

    @commands.command(hidden=True, description="Grant a user title")
    async def grant_title(self, ctx, user: discord.User, *, title):
        """Give someone access to a title (currently just sets their title)"""
        profile = self.database.get_user(user.id)
        if not profile:
            raise utils.NotRegistered(user)
        if title == "None":
            title = None
        self.database.set_title(user.id, title)
        await ctx.send("Title `{}` granted to {}".format(title, str(user)))

    @commands.command(hidden=True, description="Run eval on input. This is not dangerous.")
    async def eval(self, ctx, *, program):
        """Evaluate a given string as python code. Prints the return, if not empty."""
        try:
            result = str(eval(program))
            if result is not None and result is not "":
                result = re.sub(r"([`])", "\g<1>\u200b", result)
                await ctx.send("```py\n{}\n```".format(result))
        except Exception as e:
            await ctx.send("Program failed with {}: {}".format(e.__class__.__name__, e))

    @commands.command(hidden=True, description="Run exec on input. I laugh in the face of danger.")
    async def exec(self, ctx, *, program: str):
        """Execute a given string as python code. replaces `\n` with newlines and `\t` with tabs. Supports multiline"""\
            """ input, as well as triple backtick code blocks. Async await can be used raw, as input is wrapped in """\
            """an async function and error catcher."""
        if program.startswith("```"):
            program = re.sub(r"```(?:py)?", "", program, count=2)
        program = re.sub(r"(?<!\\)\\((?:\\\\)*)n", "\n", program)
        program = re.sub(r"(?<!\\)\\((?:\\\\)*)t", "\t", program)
        program = program.replace("\n", "\n        ")
        program = """
async def gyfiuqo(self, ctx):
    try:
        {program}
    except Exception as e:
        await ctx.send("Program failed with {{}}: {{}}".format(e.__class__.__name__, e))
        return
self.bot.loop.create_task(gyfiuqo(self, ctx))
""".format(program=program)
        try:
            exec(program)
        except Exception as e:
            await ctx.send("Program failed with {}: {}".format(e.__class__.__name__, e))

    @commands.command(hidden=True, description="Run a SQL statement. Weeh, Injection!")
    async def sql(self, ctx, *, statement):
        """Execute arbitrary SQL code, then print the result raw. All of it."""
        try:
            await ctx.send(self.bot.database.raw_exec(statement))
        except Exception as e:
            await ctx.send("Statement failed with {}: {}".format(e.__class__.__name__, e))

    @commands.command(hidden=True, description="Image testing. Smile!")
    async def image(self, ctx, red=0, green=0, blue=0):
        """Prints out a test image created on the spot. May eventually be useful for something."""
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
