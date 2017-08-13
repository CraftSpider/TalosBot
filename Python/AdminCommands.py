"""
    Admin Commands cog for Talos.
    Holds all commands relevant to administrator function, be it server specific or all of Talos.

    Author: CraftSpider
"""
import discord
import logging
from discord.ext import commands
from collections import defaultdict


#
# Admin Command Variables
#

# Hardcoded Admin List
ADMINS = ["CraftSpider#0269", "Tero#9063", "hiddenstorys#4900", "hiddenstorys#3008"]
# Ops list. Filled on bot load, altered through the add and remove op commands.
ops = defaultdict(lambda: [])
# Permissions list. Filled on bot load, altered by command
perms = {}

# Configure Logging
logging.basicConfig(level=logging.INFO)


#
# Admin Command Checks
#
def admin_check():
    """Determine whether the person calling the command is an operator or admin."""
    def predicate(ctx):
        return str(ctx.author) in ADMINS or len(ops[str(ctx.guild.id)]) == 0\
               or str(ctx.author) in ops[str(ctx.guild.id)]
    return commands.check(predicate)


def admin_only():
    """Determine whether the person calling the command is an admin."""
    def predicate(ctx):
        return str(ctx.author) in ADMINS
    return commands.check(predicate)


#
# Admin Cog Class
#
class AdminCommands:
    """These commands can only be used by Admins or Ops, and will work at any time.
    If no Ops exist, anyone can use op commands"""

    __slots__ = ['bot']

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @admin_check()
    async def nick(self, ctx, nick: str):
        """Changes Talos nickname"""
        await ctx.me.edit(nick=nick)
        await ctx.send("Nickname changed to {}".format(nick))

    @commands.command(hidden=True)
    @admin_only()
    async def playing(self, ctx, *playing: str):
        """Changes the game Talos is playing"""
        game = " ".join(map(str, playing))
        await self.bot.change_presence(game=discord.Game(name=game, type="0"))
        await ctx.send("Now playing {}".format(game))

    @commands.command(hidden=True)
    @admin_only()
    async def stop(self, ctx):
        """Stops Talos running and logs it out."""
        await ctx.send("Et Tu, Brute?")
        await self.bot.logout()

    @commands.command(hidden=True)
    @admin_only()
    async def master_nick(self, ctx, nick: str):
        """Changes Talos nickname in all servers"""
        for guild in self.bot.guilds:
            await guild.me.edit(nick=nick)
        await ctx.send("Nickname universally changed to {}".format(nick))

    @commands.command(hidden=True)
    @admin_only()
    async def all_ops(self, ctx):
        """Displays all operators everywhere"""
        out = "```"
        for key in ops:
            out += "Server: {}\n".format(key)
            for user in ops[key]:
                out += "    {}\n".format(user)
        if out != "```":
            out += "```"
            await ctx.send(out)
        else:
            await ctx.send("No ops currently")

    @commands.command()
    @admin_check()
    async def oplist(self, ctx):
        """Displays all operators for the current server"""
        if ops[str(ctx.guild.id)]:
            out = "```"
            for op in ops[str(ctx.guild.id)]:
                out += "{}\n".format(op)
            out += "```"
            await ctx.send(out)
        else:
            await ctx.send("This server currently has no operators.")

    @commands.command()
    @admin_check()
    async def add_op(self, ctx, member: discord.Member):
        """Adds a new operator user"""
        if str(member) not in ops[str(ctx.guild.id)]:
            ops[str(ctx.guild.id)].append(str(member))
            await ctx.send("Opped {0.name}!".format(member))
            await self.bot.save()
        else:
            await ctx.send("That user is already an op!")

    @commands.command(aliases=["de_op"])
    @admin_check()
    async def remove_op(self, ctx, member: discord.Member):
        """Removes an operator user"""
        try:
            ops[str(ctx.guild.id)].remove(str(member))
            await ctx.send("De-opped {0.name}".format(member))
            await self.bot.save()
        except ValueError:
            await ctx.send("That person isn't an op!")

    @commands.command()
    @admin_check()
    async def perms(self, ctx, command: str, level: str, *options):
        """Change permissions for other commands."""
        level = level.lower()
        if command in self.bot.commands:
            if level == "user":
                pass
            elif level == "channel":
                pass
            elif level == "role":
                pass
            elif level == "server":
                pass
            else:
                await ctx.send("Unrecognized permission level.")
        else:
            await ctx.send("I don't recognize that command, so I can't set permissions for it!")


def setup(bot):
    bot.add_cog(AdminCommands(bot))
