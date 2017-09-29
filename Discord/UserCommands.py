"""
    User Commands cog for Talos
    Holds all user specific commands, those things that alter a user's permissions, roles,
    Talos' knowledge of them, so on.

    Author: CraftSpider
"""
import discord
import logging
import asyncio
from discord.ext import commands

# Ops list. Filled on bot load, altered through the add and remove op commands.
ops = {}
# Permissions list. Filled on bot load, altered by command
perms = {}
# Options list. Filled on bot load, altered by command.
options = {}


def perms_check():
    """Determine whether the person calling the command is an operator or admin."""

    def predicate(ctx):

        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            return True
        guild_id = str(ctx.guild.id)
        command = str(ctx.command)

        if not options[guild_id]["UserCommands"]:
            return False
        if command not in perms[guild_id].keys():
            return True
        if "user" in perms[guild_id][command].keys():
            for key in perms[guild_id][command]["user"].keys():
                if key == str(ctx.author):
                    return perms[guild_id][command]["user"][key]
        if "role" in perms[guild_id][command].keys():
            for key in perms[guild_id][command]["role"].keys():
                for role in ctx.author.roles:
                    if key == str(role):
                        return perms[guild_id][command]["role"][key]
        if "channel" in perms[guild_id][command].keys():
            for key in perms[guild_id][command]["channel"].keys():
                if key == str(ctx.channel):
                    return perms[guild_id][command]["channel"][key]
        if "guild" in perms[guild_id][command].keys():
            return perms[guild_id][command]["guild"]
        return True

    return commands.check(predicate)


class UserCommands:
    """These commands can be used by anyone, as long as Talos is awake.\n"""\
        """The effects will apply to the person using the command."""

    __slots__ = ['bot']

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @perms_check()
    async def color(self, ctx, color: str):
        """Changes the User's color, if Talos has role permissions."""\
            """ Input must be a hexadecimal color or the word 'clear' to remove all Talos colors."""
        color_role = None
        if color == "clear":
            for role in ctx.author.roles:
                if role.name.startswith("<TALOS COLOR>"):
                    await ctx.author.remove_roles(role)
            await ctx.send("Talos color removed")
            return

        if not color.startswith("#") or len(color) is not 7 and len(color) is not 4:
            await ctx.send("That isn't a valid hexadecimal color!")
            return

        for role in ctx.author.roles:
            if role.name.startswith("<TALOS COLOR>"):
                await ctx.author.remove_roles(role)

        discord_color = None
        try:
            if len(color) == 7:
                discord_color = discord.Colour(int(color[1:], 16))
            elif len(color) == 4:
                color = color[1:]
                result = ""
                for item in color:
                    result += item*2
                discord_color = discord.Colour(int(result, 16))
                color = "#{}".format(result)
        except ValueError:
            await ctx.send("That isn't a valid hexadecimal color!")
            return

        for role in ctx.guild.roles:
            if role.name.startswith("<TALOS COLOR>") and role.color == discord_color:
                color_role = role
        if color_role is not None:
            await ctx.author.add_roles(color_role)
        else:
            color_role = await ctx.guild.create_role(name="<TALOS COLOR>", color=discord_color)
            try:
                await asyncio.sleep(.1)
                await color_role.edit(position=(ctx.guild.me.top_role.position - 1))
            except discord.errors.InvalidArgument as e:
                logging.error(e.__cause__)
                logging.error(e.args)
            await ctx.author.add_roles(color_role)

        await ctx.send("{0.name}'s color changed to {1}!".format(ctx.message.author, color))

    @commands.command()
    @perms_check()
    async def my_perms(self, ctx):
        """Has Talos print out your current guild permissions"""
        userPerms = ctx.author.guild_permissions
        out = "```Guild Permissions:\n"
        out += "    Administrator: {}\n".format(userPerms.administrator)
        out += "    Add Reactions: {}\n".format(userPerms.add_reactions)
        out += "    Attach Files: {}\n".format(userPerms.attach_files)
        out += "    Ban Members: {}\n".format(userPerms.ban_members)
        out += "    Change Nickname: {}\n".format(userPerms.change_nickname)
        out += "    Connect: {}\n".format(userPerms.connect)
        out += "    Deafen Members: {}\n".format(userPerms.deafen_members)
        out += "    Embed Links: {}\n".format(userPerms.embed_links)
        out += "    External Emojis: {}\n".format(userPerms.external_emojis)
        out += "    Instant Invite: {}\n".format(userPerms.create_instant_invite)
        out += "    Kick Members: {}\n".format(userPerms.kick_members)
        out += "    Manage Channels: {}\n".format(userPerms.manage_channels)
        out += "    Manage Emojis: {}\n".format(userPerms.manage_emojis)
        out += "    Manage Guild: {}\n".format(userPerms.manage_guild)
        out += "    Manage Messages: {}\n".format(userPerms.manage_messages)
        out += "    Manage Nicknames: {}\n".format(userPerms.manage_nicknames)
        out += "    Manage Roles: {}\n".format(userPerms.manage_roles)
        out += "    Manage Webhooks: {}\n".format(userPerms.manage_webhooks)
        out += "    Mention Everyone: {}\n".format(userPerms.mention_everyone)
        out += "    Move Members: {}\n".format(userPerms.move_members)
        out += "    Mute Members: {}\n".format(userPerms.mute_members)
        out += "    Read Message History: {}\n".format(userPerms.read_message_history)
        out += "    Read Messages: {}\n".format(userPerms.read_messages)
        out += "    Send Messages: {}\n".format(userPerms.send_messages)
        out += "    Send TTS: {}\n".format(userPerms.send_tts_messages)
        out += "    Speak: {}\n".format(userPerms.speak)
        out += "    Use Voice Activation: {}\n".format(userPerms.use_voice_activation)
        out += "    View Audit: {}\n".format(userPerms.view_audit_log)
        out += "```"
        await ctx.send(out)
    
    
def setup(bot):
    bot.add_cog(UserCommands(bot))
