"""
    Dev Commands cog for Talos.
    Holds all commands relevant to dev functions, things to alter all of Talos.

    Author: CraftSpider
"""

import discord
import discord.ext.commands as commands
import logging
import re
import io
import utils
import utils.dutils as dutils
import asyncio

from datetime import datetime
from PIL import Image, ImageDraw

# Configure Logging
log = logging.getLogger("talos.dev")


#
# Dev Cog Class
#
class DevCommands(dutils.TalosCog, command_attrs=dict(hidden=True)):
    """These commands can only be used by Talos Devs, and will work at any time. Several of them are very """\
        """dangerous. Also, they are all hidden from the help command, thus why there's no list here."""

    cog_check = dutils.dev_local

    def __getattr__(self, item):
        """
            Cog specific getattr to attempt resolving other cog names. Basically a dynamic alias system.
        :param item: Name of the attribute to get
        :return: Cog instance if one exists on the bot
        """
        cog = self.bot.cogs.get(utils.to_camel_case(item))
        if cog is None:
            raise AttributeError
        return cog

    @commands.command(description="Change what Talos is playing")
    async def playing(self, ctx, *, playing):
        """Changes what Talos is playing, the thing displayed under the name in the user list."""
        await self.bot.change_presence(activity=discord.Game(name=playing))
        await ctx.send(f"Now playing {playing}")

    @commands.command(description="Change what Talos is streaming")
    async def streaming(self, ctx, *, streaming):
        """Changes what Talos is streaming, the thing displayed under the name in the user list."""
        await self.bot.change_presence(
            activity=discord.Streaming(name=streaming, url="http://www.twitch.tv/talos_bot_", type=1))
        await ctx.send(f"Now streaming {streaming}")

    @commands.command(description="Change what Talos is listening to")
    async def listening(self, ctx, *, listening):
        """Changes what Talos is listening to, the thing displayed under the name in the user list."""
        await self.bot.change_presence(activity=discord.Activity(name=listening, type=discord.ActivityType.listening))
        await ctx.send(f"Now listening to {listening}")

    @commands.command(description="Change what Talos is watching")
    async def watching(self, ctx, *, watching):
        """Changes what Talos is watching, the thing displayed under the name in the user list."""
        await self.bot.change_presence(activity=discord.Activity(name=watching, type=discord.ActivityType.watching))
        await ctx.send(f"Now watching {watching}")

    @commands.command(description="Kills Talos process. Speak, hands for me!")
    async def stop(self, ctx):
        """Stops Talos running and logs it out safely, killing the Talos process."""
        await ctx.send("Et tū, Brute?")
        await self.bot.logout()

    log_channels = {}

    @commands.command(description="Toggle Talos logging to the current channel")
    async def loghere(self, ctx):
        """Will toggle on/off Talos sending its log messages to the current channel in addition to its normal """\
            """logfiles."""
        t = logging.getLogger("talos")
        if ctx.channel.id in self.log_channels:
            h = self.log_channels[ctx.channel.id]
            h.stop()
            t.removeHandler(h)
            await ctx.send("No longer logging here")
        else:
            h = dutils.DiscordHandler(ctx)
            h.setFormatter(logging.Formatter("`%(levelname)s:%(name)s:%(message)s`"))
            self.log_channels[ctx.channel.id] = h
            t.addHandler(h)
            await ctx.send("Started logging here")

    @commands.command(description="Change Talos' nickname everywhere. Never use this.")
    async def master_nick(self, ctx, nick):
        """Sets Talos' nickname in all guilds it is in."""
        for guild in self.bot.guilds:
            await guild.me.edit(nick=nick)
        await ctx.send(f"Nickname universally changed to {nick}")

    @commands.command(description="Verify Schema. Because updating by hand is hell.")
    async def verifysql(self, ctx):
        """Check connected SQL database schema, if it doesn't match the expected schema then alter it to fit."""
        await ctx.send("Verifying Talos Schema...")
        results = self.bot.database.verify_schema()
        schema = self.bot.database._schema
        tables = results["tables"]
        columns_add = results["columns_add"]
        columns_remove = results["columns_remove"]
        if tables == 0 and columns_add == 0 and columns_remove == 0:
            await ctx.send(f"Talos Schema {schema} verified. Everything up-to-date")
        else:
            out = f"Talos Schema {schema} verified."
            if tables:
                out += f"\n\t{tables} tables created"
            if columns_add:
                out += f"\n\t{columns_add} columns added"
            if columns_remove:
                out += f"\n\t{columns_remove} columns removed"
            await ctx.send(out)

    @commands.command(description="Grant a user title. I knight thee...")
    async def grant_title(self, ctx, user: discord.User, *, title):
        """Give someone access to a title"""
        profile = self.database.get_user(user.id)
        if not profile:
            raise dutils.NotRegistered(user)
        profile.add_title(title)
        self.database.save_item(profile)
        await ctx.send(f"Title `{title}` granted to {user}")

    @commands.command(description="Remove a title from a user. Now go in disgrace.")
    async def revoke_title(self, ctx, user: discord.User, *, title):
        """Removes access to a specific title from a user"""
        profile = self.database.get_user(user.id)
        if not profile:
            raise dutils.NotRegistered(user)
        profile.remove_title(title)
        self.database.save_item(profile)
        await ctx.send(f"Title `{title}` revoked from {user}")

    @commands.command(description="Reload a Talos extension. Allows command updates without reboot.")
    async def reload(self, ctx, name):
        """Will reload a given extension. Name should match class name exactly. Any extension can be reloaded."""
        try:
            self.bot.unload_extension(name)
        except commands.ExtensionNotLoaded:
            await ctx.send("Extension wasn't loaded, loading fresh")
        try:
            self.bot.load_extension(name)
        except commands.ExtensionNotFound:
            await ctx.send("That extension doesn't exist.")
        else:
            await ctx.send("Extension reloaded successfully.")

    @commands.command(description="Run eval on input. This is not dangerous.")
    async def eval(self, ctx, *, program):
        """Evaluate a given string as python code. Prints the return, if not empty."""
        try:
            result = str(eval(program))
            if result is not None and result is not "":
                result = re.sub(r"([`])", "\\g<1>\u200b", result)
                await ctx.send_paginated(result, prefix="```py")
        except Exception as e:
            await ctx.send(f"Program failed with {type(e).__name__}: {e}")

    @commands.command(description="Run exec on input. I laugh in the face of danger.")
    async def exec(self, ctx, *, program: str = None):
        """Execute a given string as python code. replaces `\\n` with newlines and `\\t` with tabs. Supports """\
            """multiline input, as well as triple backtick code blocks. Async await can be used raw, as input is """\
            """wrapped in an async function and error catcher."""
        if program is None and hasattr(self, "last_exec"):
            await ctx.send("Re-running last exec...")
            program = self.last_exec

        if program is None:
            await ctx.send("No prior exec to run")
            return

        program = program.strip()
        self.last_exec = program

        if program.startswith("```"):
            program = re.sub(r"```(?:py)?", "", program, count=2)
        program = re.sub(r"(?<!\\)\\((?:\\\\)*)t", "\t", program)
        program = program.replace("\n", "\n        ")
        program = f"""
async def __(self, ctx):
    import sys, io
    sys.stdout = io.StringIO()
    try:
        {program}
    except Exception as e:
        await ctx.send(f"Program failed with {{type(e).__name__}}: {{e}}")
    else:
        await ctx.send_paginated(sys.stdout.getvalue())
    finally:
        sys.stdout = sys.__stdout__
self.bot.loop.create_task(__(self, ctx))
"""
        try:
            exec(program)
        except Exception as e:
            await ctx.send(f"Program failed with {type(e).__name__}: {e}")

    @commands.command(description="Run a SQL statement. Weeh, Injection!")
    async def sql(self, ctx, *, statement):
        """Execute arbitrary SQL code, then print the result raw. All of it."""
        try:
            await ctx.send(self.bot.database.raw_exec(statement))
        except Exception as e:
            await ctx.send(f"Statement failed with {type(e).__name__}: {e}")

    @commands.command(description="Close and reopen the SQL database connection. Whoops.")
    async def resetsql(self, ctx):
        """Closes and deletes the current TalosDatabase, then attempts to open a new one."""
        await ctx.send("Reconnecting to SQL Database...")
        ctx.bot.database.reset_connection()
        await ctx.send("SQL Database Reconnection complete")

    @commands.command(description="Image testing. Smile!")
    async def image(self, ctx, red: int=0, green: int=0, blue: int=0):
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
        await asyncio.sleep(.1)
        await ctx.send(end - start)

    @commands.command(description="General test command. Does whatever it needs to")
    async def devtest(self, ctx):
        """Runs a dev test of some kind. Changes as needed to do whatever is needed, based on what internal thing I """\
            """want to test. Currently, it runs the commands_dict and prints the result. This doc may not always be """\
            """up-to-date."""
        print(self.bot.commands_dict())
        await ctx.send(len(str(self.bot.commands_dict())))


def setup(bot):
    """
        Sets up the DevCommands extension. Adds the DevCommands cog to the bot
    :param bot: Bot this extension is being setup for
    """
    bot.add_cog(DevCommands(bot))
