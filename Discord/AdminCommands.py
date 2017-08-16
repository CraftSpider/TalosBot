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
ADMINS = ["CraftSpider#0269", "Tero#9063", "hiddenstorys#4900", "Hidd/Metallic#3008", "hiddenstorys#3008"]
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

    @commands.command()
    @admin_check()
    async def repeat(self, ctx, *text):
        """Causes Talos to repeat whatever you said"""
        await ctx.send(" ".join(text))

    @commands.command()
    @admin_check()
    async def my_perms(self, ctx):
        """Has Talos print out their current permissions"""
        perms = ctx.me.guild_permissions
        out = "```Permissions:\n"
        out += "    Administrator: {}\n".format(perms.administrator)
        out += "    Add Reactions: {}\n".format(perms.add_reactions)
        out += "    Attach Files: {}\n".format(perms.attach_files)
        out += "    Ban Members: {}\n".format(perms.ban_members)
        out += "    Change Nickname: {}\n".format(perms.change_nickname)
        out += "    Connect: {}\n".format(perms.connect)
        out += "    Deafen Members: {}\n".format(perms.deafen_members)
        out += "    Embed Links: {}\n".format(perms.embed_links)
        out += "    External Emojis: {}\n".format(perms.external_emojis)
        out += "    Instant Invite: {}\n".format(perms.create_instant_invite)
        out += "    Kick Members: {}\n".format(perms.kick_members)
        out += "    Manage Channels: {}\n".format(perms.manage_channels)
        out += "    Manage Emojis: {}\n".format(perms.manage_emojis)
        out += "    Manage Guild: {}\n".format(perms.manage_guild)
        out += "    Manage Messages: {}\n".format(perms.manage_messages)
        out += "    Manage Nicknames: {}\n".format(perms.manage_nicknames)
        out += "    Manage Roles: {}\n".format(perms.manage_roles)
        out += "    Manage Webhooks: {}\n".format(perms.manage_webhooks)
        out += "    Mention Everyone: {}\n".format(perms.mention_everyone)
        out += "    Move Members: {}\n".format(perms.move_members)
        out += "    Mute Members: {}\n".format(perms.mute_members)
        out += "    Read Message History: {}\n".format(perms.read_message_history)
        out += "    Read Messages: {}\n".format(perms.read_messages)
        out += "    Send Messages: {}\n".format(perms.send_messages)
        out += "    Send TTS: {}\n".format(perms.send_tts_messages)
        out += "    Speak: {}\n".format(perms.speak)
        out += "    Use Voice Activation: {}\n".format(perms.use_voice_activation)
        out += "    View Audit: {}\n".format(perms.view_audit_log)
        out += "```"
        await ctx.send(out)

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
            out += "Server: {}\n".format(self.bot.get_guild(int(key)))
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
