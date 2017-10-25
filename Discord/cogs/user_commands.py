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

logging = logging.getLogger("talos.user")


def perms_check():
    """Determine whether the person calling the command is an operator or admin."""

    def predicate(ctx):

        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            return True
        command = str(ctx.command)

        if not ctx.bot.get_guild_option(ctx.guild.id, "user_commands"):
            return False
        perms = ctx.bot.get_perm_rules(ctx.guild.id, command)
        if len(perms) == 0:
            return True
        perms.sort(key=lambda x: x[3])
        for perm in perms:
            if perm[1] == "user" and perm[2] == str(ctx.author):
                return perm[4]
            elif perm[1] == "role":
                for role in ctx.author.roles:
                    if perm[2] == str(role):
                        return perm[4]
            elif perm[1] == "channel" and perm[2] == str(ctx.channel):
                return perm[4]
            elif perm[1] == "guild":
                return perm[4]
        return True

    return commands.check(predicate)


class UserCommands:
    """These commands can be used by anyone, as long as Talos is awake.\n"""\
        """The effects will apply to the person using the command."""

    __slots__ = ['bot']

    def __init__(self, bot):
        """Initialize the UserCommands cog. Takes in an instance of Talos to use while running."""
        self.bot = bot

    @commands.command()
    @commands.guild_only()
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
    @commands.guild_only()
    @perms_check()
    async def my_perms(self, ctx):
        """Has Talos print out your current guild permissions"""
        user_perms = ctx.author.guild_permissions
        out = "```Guild Permissions:\n"
        out += "    Administrator: {}\n".format(user_perms.administrator)
        out += "    Add Reactions: {}\n".format(user_perms.add_reactions)
        out += "    Attach Files: {}\n".format(user_perms.attach_files)
        out += "    Ban Members: {}\n".format(user_perms.ban_members)
        out += "    Change Nickname: {}\n".format(user_perms.change_nickname)
        out += "    Connect: {}\n".format(user_perms.connect)
        out += "    Deafen Members: {}\n".format(user_perms.deafen_members)
        out += "    Embed Links: {}\n".format(user_perms.embed_links)
        out += "    External Emojis: {}\n".format(user_perms.external_emojis)
        out += "    Instant Invite: {}\n".format(user_perms.create_instant_invite)
        out += "    Kick Members: {}\n".format(user_perms.kick_members)
        out += "    Manage Channels: {}\n".format(user_perms.manage_channels)
        out += "    Manage Emojis: {}\n".format(user_perms.manage_emojis)
        out += "    Manage Guild: {}\n".format(user_perms.manage_guild)
        out += "    Manage Messages: {}\n".format(user_perms.manage_messages)
        out += "    Manage Nicknames: {}\n".format(user_perms.manage_nicknames)
        out += "    Manage Roles: {}\n".format(user_perms.manage_roles)
        out += "    Manage Webhooks: {}\n".format(user_perms.manage_webhooks)
        out += "    Mention Everyone: {}\n".format(user_perms.mention_everyone)
        out += "    Move Members: {}\n".format(user_perms.move_members)
        out += "    Mute Members: {}\n".format(user_perms.mute_members)
        out += "    Read Message History: {}\n".format(user_perms.read_message_history)
        out += "    Read Messages: {}\n".format(user_perms.read_messages)
        out += "    Send Messages: {}\n".format(user_perms.send_messages)
        out += "    Send TTS: {}\n".format(user_perms.send_tts_messages)
        out += "    Speak: {}\n".format(user_perms.speak)
        out += "    Use Voice Activation: {}\n".format(user_perms.use_voice_activation)
        out += "    View Audit: {}\n".format(user_perms.view_audit_log)
        out += "```"
        await ctx.send(out)

    @commands.command()
    @perms_check()
    async def register(self, ctx):
        """TODO, Registers you as a user with Talos. This creates a profile and options for you, and allows Talos to"""\
            """save info."""
        await ctx.send("Not yet implemented")

    @commands.command()
    @perms_check()
    async def profile(self, ctx, user: discord.User=None):
        """TODO, Displays you or another user's profile, if it exists."""
        print(user)
        await ctx.send("Not yet implemented")

    @commands.group()
    @perms_check()
    async def user(self, ctx):
        """TODO, No current use"""
        await ctx.send("Not yet implemented")

    
def setup(bot):
    bot.add_cog(UserCommands(bot))
