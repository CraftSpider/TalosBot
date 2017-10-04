"""
    Admin Commands cog for Talos.
    Holds all commands relevant to administrator function, be it server specific or all of Talos.

    Author: CraftSpider
"""
import discord
import logging
import random
import string
import re
from discord.ext import commands
from collections import defaultdict


#
# Admin Command Variables
#

# Hardcoded Admin List
ADMINS = ["CraftSpider#0269", "Tero#9063", "hiddenstorys#4900", "Hidd/Metallic#3008", "hiddenstorys#3008"]
# Ops list. Filled on bot load, altered through the add and remove op commands.
ops = {}
# Permissions list. Filled on bot load, altered by command
perms = {}
# Options list. Filled on bot load, altered by command.
options = {}
# Security keys, for security-locked commands.
secure_keys = defaultdict(lambda: "")

# Configure Logging
logging = logging.getLogger("talos.admin")


def key_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """Generates random strings for things that need keys. Allows variable size and character lists, if desired."""
    return ''.join(random.choice(chars) for _ in range(size))


def set_perm(guild, command, level, allow, name=None):
    """Sets the permissions for given inputs"""
    if name is not None:
        try:
            perms[guild][command][level][name] = allow
        except KeyError:
            if command not in perms[guild].keys():
                perms[guild][command] = {}
            if level not in perms[guild][command].keys():
                perms[guild][command][level] = {}
            perms[guild][command][level][name] = allow
    else:
        try:
            perms[guild][command][level] = allow
        except KeyError:
            if command not in perms[guild].keys():
                perms[guild][command] = {}
            perms[guild][command][level] = allow


def remove_perm(guild, command, level=None, name=None):
    """Clears the permissions, for given inputs."""
    if name is not None:
        del perms[guild][command][level][name]
        if len(perms[guild][command][level]) == 0:
            del perms[guild][command][level]
        if len(perms[guild][command]) == 0:
            del perms[guild][command]
    elif level is not None:
        del perms[guild][command][level]
        if len(perms[guild][command]) == 0:
            del perms[guild][command]
    else:
        del perms[guild][command]


def space_replace(match):
    print(match.group(1))
    if match.group(1):
        return "\\"*int(len(match.group(0)) / 2) + " "
    else:
        return " "


#
# Admin Command Checks
#
def op_check():
    """Determine whether the person calling the command is an operator or admin."""
    def predicate(ctx):

        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            return True
        guild_id = str(ctx.guild.id)
        command = str(ctx.command)

        if str(ctx.author) in ADMINS or\
           len(ops[guild_id]) == 0 and ctx.author.guild_permissions.administrator or\
           ctx.author == ctx.guild.owner or\
           str(ctx.author) in ops[guild_id]:
            return True

        if command not in perms[guild_id].keys():
            return False
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
        return False

    return commands.check(predicate)


def admin_check():
    """Determine whether the person calling the command is an admin."""
    def predicate(ctx):
        return str(ctx.author) in ADMINS
    return commands.check(predicate)


#
# Admin Cog Class
#
class AdminCommands:
    """These commands can only be used by Admins or Ops, and will work at any time.
    If no Ops exist, anyone with admin can use op commands"""

    __slots__ = ['bot']

    LEVELS = {"guild": 0, "channel": 1, "role": 2, "user": 3}

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @op_check()
    async def nick(self, ctx, nick: str):
        """Changes Talos nickname"""
        await ctx.me.edit(nick=nick)
        await ctx.send("Nickname changed to {}".format(nick))

    @commands.command()
    @op_check()
    async def repeat(self, ctx, *text):
        """Causes Talos to repeat whatever you said"""
        if len(text) is not 0:
            await ctx.send(" ".join(text))

    @commands.command(usage="[number=10]")
    @commands.guild_only()
    @op_check()
    async def purge(self, ctx, number: str="10", *key):
        """Purges messages from a channel. By default, this will be 10 (including the invoking command)."""\
            """ Use 'all' to purge whole channel."""
        if number != "all":
            number = int(number)
            if number >= 100 and (len(key) == 0 or key[0] != secure_keys[str(ctx.guild.id)]):
                rand_key = key_generator()
                secure_keys[str(ctx.guild.id)] = rand_key
                await ctx.send("Are you sure? If so, re-invoke with {} on the end.".format(rand_key))
            else:
                await ctx.channel.purge(limit=number)
        else:
            if len(key) == 0 or key[0] != secure_keys[str(ctx.guild.id)]:
                rand_key = key_generator()
                secure_keys[str(ctx.guild.id)] = rand_key
                await ctx.send("Are you sure? If so, re-invoke with {} on the end.".format(rand_key))
            elif key[0] == secure_keys[str(ctx.guild.id)]:
                await ctx.channel.purge(limit=None)
                secure_keys[str(ctx.guild.id)] = ""

    @commands.command()
    @commands.guild_only()
    @op_check()
    async def talos_perms(self, ctx):
        """Has Talos print out their current guild permissions"""
        talosPerms = ctx.me.guild_permissions
        out = "```Guild Permissions:\n"
        out += "    Administrator: {}\n".format(talosPerms.administrator)
        out += "    Add Reactions: {}\n".format(talosPerms.add_reactions)
        out += "    Attach Files: {}\n".format(talosPerms.attach_files)
        out += "    Ban Members: {}\n".format(talosPerms.ban_members)
        out += "    Change Nickname: {}\n".format(talosPerms.change_nickname)
        out += "    Connect: {}\n".format(talosPerms.connect)
        out += "    Deafen Members: {}\n".format(talosPerms.deafen_members)
        out += "    Embed Links: {}\n".format(talosPerms.embed_links)
        out += "    External Emojis: {}\n".format(talosPerms.external_emojis)
        out += "    Instant Invite: {}\n".format(talosPerms.create_instant_invite)
        out += "    Kick Members: {}\n".format(talosPerms.kick_members)
        out += "    Manage Channels: {}\n".format(talosPerms.manage_channels)
        out += "    Manage Emojis: {}\n".format(talosPerms.manage_emojis)
        out += "    Manage Guild: {}\n".format(talosPerms.manage_guild)
        out += "    Manage Messages: {}\n".format(talosPerms.manage_messages)
        out += "    Manage Nicknames: {}\n".format(talosPerms.manage_nicknames)
        out += "    Manage Roles: {}\n".format(talosPerms.manage_roles)
        out += "    Manage Webhooks: {}\n".format(talosPerms.manage_webhooks)
        out += "    Mention Everyone: {}\n".format(talosPerms.mention_everyone)
        out += "    Move Members: {}\n".format(talosPerms.move_members)
        out += "    Mute Members: {}\n".format(talosPerms.mute_members)
        out += "    Read Message History: {}\n".format(talosPerms.read_message_history)
        out += "    Read Messages: {}\n".format(talosPerms.read_messages)
        out += "    Send Messages: {}\n".format(talosPerms.send_messages)
        out += "    Send TTS: {}\n".format(talosPerms.send_tts_messages)
        out += "    Speak: {}\n".format(talosPerms.speak)
        out += "    Use Voice Activation: {}\n".format(talosPerms.use_voice_activation)
        out += "    View Audit: {}\n".format(talosPerms.view_audit_log)
        out += "```"
        await ctx.send(out)

    @commands.command(hidden=True)
    @admin_check()
    async def playing(self, ctx, *playing: str):
        """Changes the game Talos is playing"""
        game = " ".join(map(str, playing))
        await self.bot.change_presence(game=discord.Game(name=game))
        await ctx.send("Now playing {}".format(game))

    @commands.command(hidden=True)
    @admin_check()
    async def streaming(self, ctx, *streaming: str):
        """Changes the game Talos is streaming"""
        game = " ".join(map(str, streaming))
        await self.bot.change_presence(game=discord.Game(name=game, url="http://www.twitch.tv/CraftSpider",  type=1))
        await ctx.send("Now streaming {}".format(game))

    @commands.command(hidden=True)
    @admin_check()
    async def stop(self, ctx):
        """Stops Talos running and logs it out."""
        await ctx.send("Et tū, Brute?")
        await self.bot.logout()

    @commands.command(hidden=True)
    @admin_check()
    async def master_nick(self, ctx, nick: str):
        """Changes Talos nickname in all servers"""
        for guild in self.bot.guilds:
            await guild.me.edit(nick=nick)
        await ctx.send("Nickname universally changed to {}".format(nick))

    @commands.command(hidden=True)
    @admin_check()
    async def verify(self, ctx):
        added, removed = await self.bot.verify()
        await ctx.send("Data Verified. {} objects added, {} objects removed.".format(added, removed))

    @commands.group()
    @op_check()
    async def ops(self, ctx):
        """Operator related commands. By default, anyone on a server with admin privileges is an Op."""\
            """ Adding someone to the list will override this behavior.
            The Server Owner is also always Op, and this behavior can't be overridden for security reasons."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'add', 'list', and 'remove'.")

    @ops.command(name="add")
    @commands.guild_only()
    async def _ops_add(self, ctx, member: discord.Member):
        """Adds a new operator user"""
        if str(member) not in ops[str(ctx.guild.id)]:
            ops[str(ctx.guild.id)].append(str(member))
            await self.bot.update(newOps=ops)
            await ctx.send("Opped {0.name}!".format(member))
        else:
            await ctx.send("That user is already an op!")

    @ops.command(name="remove")
    @commands.guild_only()
    async def _ops_remove(self, ctx, member: discord.Member):
        """Removes an operator user"""
        try:
            ops[str(ctx.guild.id)].remove(str(member))
            await self.bot.update(newOps=ops)
            await ctx.send("De-opped {0.name}".format(member))
        except ValueError:
            await ctx.send("That person isn't an op!")

    @ops.command(name="list")
    @commands.guild_only()
    async def _ops_list(self, ctx):
        """Displays all operators for the current server"""
        if ops[str(ctx.guild.id)]:
            out = "```"
            for op in ops[str(ctx.guild.id)]:
                out += "{}\n".format(op)
            out += "```"
            await ctx.send(out)
        else:
            await ctx.send("This server currently has no operators.")

    @ops.command(name="all", hidden=True)
    @admin_check()
    async def _ops_all(self, ctx):
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

    @commands.group()
    @op_check()
    async def perms(self, ctx):
        """Permissions related commands. Talos permissions currently are divided into 4 levels, with each level """\
           """overriding any lower one. The levels, in order from lowest to highest priority, are:
           -Guild
           -Channel
           -Role
           -User
           One can 'allow' or 'forbid' specifics at each level, or simply 'allow' or 'forbid' the whole guild."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'create', 'list', and 'remove'.")

    @perms.command(name="create")
    @commands.guild_only()
    async def _p_create(self, ctx, command: str, level: str, allow: str, name: str=None):
        """Create or alter a permissions rule. Provide a command, one of the four levels, whether to allow or """\
            """forbid, and if the level isn't guild, a name."""
        level = level.lower()
        allow = allow.lower()
        if allow == "allow" or allow == "true":
            allow = True
        elif allow == "forbid" or allow == "false":
            allow = False
        else:
            await ctx.send("I can only 'allow' or 'forbid', sorry!")
            return

        if command in self.bot.all_commands and level in self.LEVELS:
            if name is None and level != "guild":
                await ctx.send("You need to include both a name and either 'allow' or 'forbid'")
                return

            oldName = name
            if level == "user":
                name = discord.utils.find(lambda u: u.name == name, ctx.guild.members)
            elif level == "role":
                name = discord.utils.find(lambda r: r.name == name, ctx.guild.roles)
            elif level == "channel":
                name = discord.utils.find(lambda c: c.name == name, ctx.guild.channels)
            elif level == "guild":
                name = ""
            if name is None:
                await ctx.send("Sorry, I couldn't find the user {}!".format(oldName))
                return
            name = str(name) if name != "" else None
            set_perm(str(ctx.guild.id), command, level, allow, name)
            await self.bot.update(newPerms=perms)
            await ctx.send("Permissions for command **{}** at level **{}** updated.".format(command, level))
        elif command not in self.bot.all_commands:
            await ctx.send("I don't recognize that command, so I can't set permissions for it!")
        else:
            await ctx.send("Unrecognized permission level.")

    @perms.command(name="remove")
    @commands.guild_only()
    async def _p_remove(self, ctx, command: str, *args):
        """Remove a permissions rule or set of rules."""
        if len(args) > 0:
            level = args[0]
            level = level.lower()
        else:
            level = None
        if command in self.bot.all_commands and (level in self.LEVELS or level is None):
            spec = None
            if len(args) > 1:
                if level == "user":
                    spec = str(discord.utils.find(lambda u: u.name == args[1], ctx.guild.members))
                elif level == "role":
                    spec = str(discord.utils.find(lambda r: r.name == args[1], ctx.guild.roles))
                elif level == "channel":
                    spec = str(discord.utils.find(lambda c: c.name == args[1], ctx.guild.channels))

            remove_perm(str(ctx.guild.id), command, level, spec)
            await self.bot.update(newPerms=perms)
            if level is None:
                await ctx.send("Permissions for command **{}** at all levels cleared.".format(command))
                return
            await ctx.send("Permissions for command **{}** at level **{}** cleared.".format(command, level))
        elif command not in self.bot.commands:
            await ctx.send("I don't recognize that command, so I can't clear permissions for it!")
        else:
            await ctx.send("Unrecognized permission level.")

    @perms.command(name="list")
    @commands.guild_only()
    async def _p_list(self, ctx):
        """Lists permissions rules for the current guild"""
        guild_perms = perms[str(ctx.guild.id)]
        if len(guild_perms) == 0:
            await ctx.send("No permissions set for this server.")
            return
        out = "```"
        for command in guild_perms:
            out += "Command: {}\n".format(command)
            for level in sorted(guild_perms[command], key=lambda a: self.LEVELS[a]):
                out += "    Level: {}\n".format(level)
                if level == "guild":
                    out += "        {}\n".format(guild_perms[command][level])
                else:
                    for spec in guild_perms[command][level]:
                        out += "        {}: {}\n".format(spec, guild_perms[command][level][spec])
        out += "```"
        await ctx.send(out)

    @perms.command(name="all", hidden=True)
    @admin_check()
    async def _p_all(self, ctx):
        """Displays all permissions everywhere"""
        await ctx.send("`{}`".format(perms))

    @commands.group()
    async def options(self, ctx):
        """Command to change Talos guild options. All of these only effect the current guild."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'set', 'list', and 'default'.")

    @options.command(name="set")
    @commands.guild_only()
    @op_check()
    async def _opt_set(self, ctx, option: str, value: str):
        """Set an option. Most options are true or false. See `^options list` for available options"""
        if isinstance(options[str(ctx.guild.id)][option], bool):
            if value.upper() == "ALLOW" or value.upper() == "TRUE":
                value = True
            elif value.upper() == "FORBID" or value.upper() == "FALSE":
                value = False
            else:
                await ctx.send("Sorry, that option only accepts true or false values.")
                return
        if isinstance(options[str(ctx.guild.id)][option], str):
            value = re.sub("(?<!\\\\)\\\\((?:\\\\\\\\)*)s", space_replace, value)
            value = re.sub("\\\\\\\\", "\\\\", value)
        if option in options[str(ctx.guild.id)]:
            options[str(ctx.guild.id)][option] = value
            await ctx.send("Option {} set to `{}`".format(option, value))
            await self.bot.update(newOptions=options)
        else:
            await ctx.send("I don't recognize that option.")

    @options.command(name="list")
    @commands.guild_only()
    async def _opt_list(self, ctx):
        """List of what options are currently set on the server. Do `^help options [option name]` for details on"""\
            """ an individual option"""
        out = "```"
        for key in sorted(options[str(ctx.guild.id)]):
            out += "{}: {}\n".format(key, options[str(ctx.guild.id)][key])
        out += "```"
        await ctx.send(out)

    @options.command(name="default")
    @commands.guild_only()
    @op_check()
    async def _opt_default(self, ctx, option):
        """Sets an option to its default value, as in a server Talos had just joined."""
        if option in options[str(ctx.guild.id)]:
            options[str(ctx.guild.id)][option] = self.bot.get_default(option)
            await ctx.send("Option {} set to default".format(option))
            await self.bot.update(newOptions=options)
        else:
            await ctx.send("I don't recognize that option")

    @options.command(name="all", hidden=True)
    @admin_check()
    async def _opt_all(self, ctx):
        """Displays all options everywhere"""
        out = "```"
        for key in options:
            out += "Server: {}\n".format(self.bot.get_guild(int(key)))
            for option in options[key]:
                out += "    {}\n".format(option)
        await ctx.send(out)


def setup(bot):
    bot.add_cog(AdminCommands(bot))
