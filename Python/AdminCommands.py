import discord
import logging
import asyncio
from discord.ext import commands
from collections import defaultdict

logging.basicConfig(level=logging.INFO)


ADMINS = ["CraftSpider#0269", "Tero#9063", "hiddenstorys#4900"]
ops = defaultdict(lambda: [])


def admin_check():
    def predicate(ctx):
        return str(ctx.message.author) in ADMINS or len(ops[ctx.message.server.id]) == 0\
               or str(ctx.message.author) in ops[ctx.message.server.id]
    return commands.check(predicate)


def admin_only():
    def predicate(ctx):
        return str(ctx.message.author) in ADMINS
    return commands.check(predicate)


class AdminCommands:
    """These commands can only be used by Admins or Ops, and will work at any time.
    If no Ops exist, anyone can use op commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @admin_check()
    async def nick(self, ctx, nick: str):
        """Changes Talos nickname"""
        await self.bot.change_nickname(ctx.message.server.me, nick)
        await self.bot.say("Nickname changed to {0}".format(nick))

    @commands.command(hidden=True)
    @admin_only()
    async def playing(self, *playing: str):
        """Changes the game Talos is playing"""
        game = " ".join(map(str, playing))
        await self.bot.change_presence(game=discord.Game(name=game, type="0"))
        await self.bot.say("Now playing {0}".format(game))

    @commands.command(hidden=True)
    @admin_only()
    async def stop(self):
        await self.bot.say("Et Tu, Brute?")
        await self.bot.logout()

    @commands.command(hidden=True)
    @admin_only()
    async def master_nick(self, nick: str):
        """Changes Talos nickname in all servers"""
        for server in self.bot.servers:
            await self.bot.change_nickname(server.me, nick)
        await self.bot.say("Nickname universally changed to {0}".format(nick))

    @commands.command(hidden=True)
    @admin_only()
    async def all_ops(self):
        """Displays all operators everywhere"""
        out = "```"
        for key in ops:
            out += "Server: {0}\n".format(key)
            for user in ops[key]:
                out += "    {0}\n".format(user)
        if out != "```":
            out += "```"
            await self.bot.say(out)
        else:
            await self.bot.say("No ops currently")

    @commands.command(pass_context=True)
    @admin_check()
    async def oplist(self, ctx):
        """Displays all operators for the current server"""
        if ops[ctx.message.server.id]:
            out = "```"
            for op in ops[ctx.message.server.id]:
                out += "{0}\n".format(op)
            out += "```"
            await self.bot.say(out)
        else:
            await self.bot.say("This server currently has no operators.")

    @commands.command(pass_context=True)
    @admin_check()
    async def add_op(self, ctx, member: discord.Member):
        """Adds a new operator user"""
        ops[ctx.message.server.id].append(str(member))
        await self.bot.say("Opped {0.name}!".format(member))

    @commands.command(pass_context=True)
    @admin_check()
    async def remove_op(self, ctx, member: discord.Member):
        """Removes an operator user"""
        try:
            ops[ctx.message.server.id].remove(str(member))
            await self.bot.say("De-opped {0.name}".format(member))
        except ValueError:
            await self.bot.say("That person isn't an op!")


def setup(bot):
    bot.add_cog(AdminCommands(bot))
