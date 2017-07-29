import discord
import logging
from discord.ext import commands

logging.basicConfig(level=logging.INFO)


ADMINS = ["CraftSpider#0269", "Tero#9063", "hiddenstorys#4900"]
ops = []


def admin_check():
    def predicate(ctx):
        return str(ctx.message.author) in ADMINS or len(ops) == 0 or str(ctx.message.author) in ops
    return commands.check(predicate)


def admin_only():
    def predicate(ctx):
        return str(ctx.message.author) in ADMINS
    return commands.check(predicate)


class AdminCommands:
    """These commands can only be used by Admins or Ops, and will work at any time.\nIf no Ops exist, anyone can use op commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @admin_check()
    async def nick(self, ctx, nick : str):
        """Changes Talos nickname"""
        await self.bot.change_nickname(ctx.message.server.me, nick)
        await self.bot.say("Nickname changed to {0}".format(nick))

    @commands.command(hidden=True)
    @admin_only()
    async def playing(self, *playing : str):
        """Changes the game Talos is playing"""
        await self.bot.change_presence(game=discord.Game(name=" ".join(map(str, playing)), type="0"))

    @commands.command(hidden=True)
    @admin_only()
    async def master_nick(self, nick : str):
        """Changes Talos nickname in all servers"""
        for server in self.bot.servers:
            await self.bot.change_nickname(server.me, nick)
        await self.bot.say("Nickname universally changed to {0}".format(nick))

    @commands.command()
    @admin_check()
    async def add_Op(self, member : discord.Member):
        """Adds a new operator user"""
        ops.append(str(member))
        await self.bot.say("Opped {0.name}!".format(member))

    @commands.command()
    @admin_check()
    async def remove_Op(self, member : discord.Member):
        """Removes an operator user"""
        try:
            ops.remove(str(member))
            await self.bot.say("De-opped {0.name}".format(member))
        except ValueError:
            await self.bot.say("That person isn't an op!")


def setup(bot):
    bot.add_cog(AdminCommands(bot))
