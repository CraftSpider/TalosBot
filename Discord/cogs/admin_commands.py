"""
    Admin Commands cog for Talos.
    Holds all commands relevant to administrator function, guild specific stuff.

    Author: CraftSpider
"""
import discord
import logging
import random
import string
import re
import utils
from discord.ext import commands
from collections import defaultdict


#
# Admin Command Variables
#

# Security keys, for security-locked commands.
secure_keys = defaultdict(lambda: "")

# Configure Logging
log = logging.getLogger("talos.admin")


def key_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """Generates random strings for things that need keys. Allows variable size and character lists, if desired."""
    return ''.join(random.choice(chars) for _ in range(size))


def space_replace(match):
    print(match.group(1))
    if match.group(1):
        return "\\"*int(len(match.group(0)) / 2) + " "
    else:
        return " "


#
# Admin Command Checks
#
def op_check(self, ctx):
    """Determine whether the person calling the command is an operator or admin."""
    if isinstance(ctx.channel, discord.abc.PrivateChannel):
        return True
    command = str(ctx.command)

    if ctx.author.id in ctx.bot.ADMINS or\
       len(ctx.bot.database.get_ops(ctx.guild.id)) == 0 and ctx.author.guild_permissions.administrator or\
       ctx.author == ctx.guild.owner or\
       ctx.author.id in ctx.bot.database.get_ops(ctx.guild.id):
        return True

    perms = ctx.bot.database.get_perm_rules(ctx.guild.id, command)
    if len(perms) == 0:
        return False
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
    return False


def dev_check():
    """Determine whether the person calling the command is an admin."""
    def predicate(ctx):
        return ctx.author.id in ctx.bot.ADMINS
    return commands.check(predicate)


#
# Admin Cog Class
#
class AdminCommands(utils.TalosCog):
    """These commands can only be used by Admins or Ops, and will work at any time.
    If no ops exist, anyone with admin role permission can use op commands"""

    LEVELS = {"guild": 0, "channel": 1, "role": 2, "user": 3}
    __local_check = op_check

    @commands.command(description="Changes Talos' nickname")
    @commands.guild_only()
    async def nick(self, ctx, *, nickname):
        """Sets Talos' nickname in the current guild."""
        await ctx.me.edit(nick=nickname)
        await ctx.send("Nickname changed to {}".format(nickname))

    @commands.command(description="Makes Talos repeat you")
    async def repeat(self, ctx, *, text):
        """Causes Talos to repeat whatever you just said, exactly."""
        await ctx.send(text)

    @commands.command(usage="[number=10]", description="Remove messages from a channel")
    @commands.guild_only()
    async def purge(self, ctx, number="10", *key):
        """Purges messages from a channel. By default, this will be 10 (including the invoking command)."""\
            """ Use 'all' to purge whole channel. Confirmation keys should be tacked on the end, so """\
            """`^purge 100 [key]`"""
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

    @commands.command(description="Display current Talos perms")
    @commands.guild_only()
    async def talos_perms(self, ctx):
        """Has Talos display their current effective guild permissions. This is channel independent, """\
            """channel-specific perms aren't taken into account."""
        talos_perms = ctx.me.guild_permissions
        out = "```Guild Permissions:\n"
        out += "    Administrator: {}\n".format(talos_perms.administrator)
        out += "    Add Reactions: {}\n".format(talos_perms.add_reactions)
        out += "    Attach Files: {}\n".format(talos_perms.attach_files)
        out += "    Ban Members: {}\n".format(talos_perms.ban_members)
        out += "    Change Nickname: {}\n".format(talos_perms.change_nickname)
        out += "    Connect: {}\n".format(talos_perms.connect)
        out += "    Deafen Members: {}\n".format(talos_perms.deafen_members)
        out += "    Embed Links: {}\n".format(talos_perms.embed_links)
        out += "    External Emojis: {}\n".format(talos_perms.external_emojis)
        out += "    Instant Invite: {}\n".format(talos_perms.create_instant_invite)
        out += "    Kick Members: {}\n".format(talos_perms.kick_members)
        out += "    Manage Channels: {}\n".format(talos_perms.manage_channels)
        out += "    Manage Emojis: {}\n".format(talos_perms.manage_emojis)
        out += "    Manage Guild: {}\n".format(talos_perms.manage_guild)
        out += "    Manage Messages: {}\n".format(talos_perms.manage_messages)
        out += "    Manage Nicknames: {}\n".format(talos_perms.manage_nicknames)
        out += "    Manage Roles: {}\n".format(talos_perms.manage_roles)
        out += "    Manage Webhooks: {}\n".format(talos_perms.manage_webhooks)
        out += "    Mention Everyone: {}\n".format(talos_perms.mention_everyone)
        out += "    Move Members: {}\n".format(talos_perms.move_members)
        out += "    Mute Members: {}\n".format(talos_perms.mute_members)
        out += "    Read Message History: {}\n".format(talos_perms.read_message_history)
        out += "    Read Messages: {}\n".format(talos_perms.read_messages)
        out += "    Send Messages: {}\n".format(talos_perms.send_messages)
        out += "    Send TTS: {}\n".format(talos_perms.send_tts_messages)
        out += "    Speak: {}\n".format(talos_perms.speak)
        out += "    Use Voice Activation: {}\n".format(talos_perms.use_voice_activation)
        out += "    View Audit: {}\n".format(talos_perms.view_audit_log)
        out += "```"
        await ctx.send(out)

    @commands.group(description="Operator related commands")
    async def ops(self, ctx):
        """By default, anyone on a guild with admin privileges is an Op. Adding someone to the list will override """\
            """ this behavior.
            The Guild Owner is also always Op, and this behavior can't be overridden for security reasons."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'add', 'list', and 'remove'.")

    @ops.command(name="add", description="Adds a new operator")
    @commands.guild_only()
    async def _ops_add(self, ctx, member: discord.Member):
        """Adds a user to the guild operator list."""
        if member.id not in self.database.get_ops(ctx.guild.id):
            self.database.add_op(ctx.guild.id, member.id)
            await ctx.send("Opped {0.name}!".format(member))
        else:
            await ctx.send("That user is already an op!")

    @ops.command(name="remove", description="Removes an operator")
    @commands.guild_only()
    async def _ops_remove(self, ctx, member):
        """Removes an operator user from the guild list"""
        member_object = discord.utils.find(
            lambda x: x.name == member or str(x) == member or (member.isnumeric() and x.id == int(member)),
            ctx.guild.members
        )
        if member_object is not None:
            member = member_object.id
        elif member.isnumeric():
            member = int(member)
        if member in self.database.get_ops(ctx.guild.id):
            self.database.remove_op(ctx.guild.id, member)
            if member_object:
                await ctx.send("De-opped {0.name}".format(member_object))
            else:
                await ctx.send("De-opped invalid user")
        else:
            await ctx.send("That person isn't an op!")

    @ops.command(name="list", description="Display operators")
    @commands.guild_only()
    async def _ops_list(self, ctx):
        """Displays all operators for the current guild"""
        opslist = self.database.get_ops(ctx.guild.id)
        if len(opslist) > 0:
            out = "```"
            for op in opslist:
                opname = self.bot.get_user(op)
                out += "{}\n".format(str(opname) if opname is not None else op)
            out += "```"
            await ctx.send(out)
        else:
            await ctx.send("This guild currently has no operators.")

    @ops.command(name="all", hidden=True, description="Display all operators")
    @dev_check()
    async def _ops_all(self, ctx):
        """Displays all operators in every guild Talos is in"""
        all_ops = self.database.get_all_ops()
        consumed = []
        out = "```"
        for key in all_ops:
            if key[0] not in consumed:
                out += "Guild: {}\n".format(self.bot.get_guild(key[0]))
                consumed.append(key[0])
            op = self.bot.get_user(key[1])
            out += "    {}\n".format(str(op) if op is not None else key[1])
        if out != "```":
            out += "```"
            await ctx.send(out)
        else:
            await ctx.send("No ops currently")

    @commands.group(description="Permissions related commands")
    async def perms(self, ctx):
        """Talos permissions are divided into 4 levels, with each level having a default priority. The levels, in """\
           """order from lowest to highest default priority, are:
           -Guild
           -Channel
           -Role
           -User
           If one doesn't like the default priority, it can be changed by adding a number to the end of the command."""\
           """ Priority defaults are 10 for guild, then going up by ten for each level, ending with User being 40.
           One can 'allow' or 'forbid' specifics at each level, or simply 'allow' or 'forbid' the whole guild."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'create', 'list', and 'remove'.")

    @perms.command(name="create", description="Create or alter permission rules")
    @commands.guild_only()
    async def _p_create(self, ctx, command, level, allow, name=None, priority: int=None):
        """Provide a command, one of the four levels (see `^help perms`), whether to allow or forbid the command, """\
            """a name (If level is guild, this is ignored), and a priority if you don't want default."""
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

            old_name = name
            if level == "user":
                name = discord.utils.find(lambda u: u.name == name, ctx.guild.members)
            elif level == "role":
                name = discord.utils.find(lambda r: r.name == name, ctx.guild.roles)
            elif level == "channel":
                name = discord.utils.find(lambda c: c.name == name, ctx.guild.channels)
            elif level == "guild":
                name = ""
            if name is None:
                await ctx.send("Sorry, I couldn't find the user {}!".format(old_name))
                return
            name = str(name) if name != "" else None
            self.database.set_perm_rule(ctx.guild.id, command, level, allow, priority, name)
            await ctx.send("Permissions for command **{}** at level **{}** updated.".format(command, level))
        elif command not in self.bot.all_commands:
            await ctx.send("I don't recognize that command, so I can't set permissions for it!")
        else:
            await ctx.send("Unrecognized permission level.")

    @perms.command(name="remove", description="Remove permission rules")
    @commands.guild_only()
    async def _p_remove(self, ctx, command=None, level=None, name=None):
        """Remove a permissions rule or set of rules. Be careful, as simply `^perms remove` will clear all guild """\
            """permissions."""
        if isinstance(level, str):
            level = level.lower()
        if level in self.LEVELS or level is None:
            if isinstance(name, str):
                if level == "user":
                    name = str(discord.utils.find(lambda u: u.name == name, ctx.guild.members))
                elif level == "role":
                    name = str(discord.utils.find(lambda r: r.name == name, ctx.guild.roles))
                elif level == "channel":
                    name = str(discord.utils.find(lambda c: c.name == name, ctx.guild.channels))
            self.database.remove_perm_rules(ctx.guild.id, command, level, name)
            if command is None:
                await ctx.send("Permissions for guild cleared")
                return
            if level is None:
                await ctx.send("Permissions for command **{}** at all levels cleared.".format(command))
                return
            if name is None:
                await ctx.send("Permissions for command **{}** at level **{}** cleared.".format(command, level))
                return
            out = "Permissions for command **{}** at level **{}** for **{}** cleared.".format(command, level, name)
            await ctx.send(out)
        else:
            await ctx.send("Unrecognized permission level.")

    @perms.command(name="list", description="Display permission rules for the current guild")
    @commands.guild_only()
    async def _p_list(self, ctx):
        """Displays a list of all permissions rules for the current guild"""
        result = self.database.get_perm_rules(ctx.guild.id)
        if len(result) == 0:
            await ctx.send("No permissions set for this guild, with all data about them.")
            return
        guild_perms = {}
        for line in result:
            if guild_perms.get(line[0], None) is None:
                guild_perms[line[0]] = {}
            if guild_perms.get(line[0]).get(line[1], None) is None:
                guild_perms[line[0]][line[1]] = []
            guild_perms[line[0]][line[1]].append([line[2], line[3], line[4]])

        out = "```"
        for command in guild_perms:
            out += "Command: {}\n".format(command)
            for level in sorted(guild_perms[command], key=lambda a: self.LEVELS[a]):
                out += "    Level: {}\n".format(level)
                if level == "guild":
                    out += "        {}\n".format(guild_perms[command][level])
                else:
                    for detail in guild_perms[command][level]:
                        out += "        {1}-{0}: {2}\n".format(detail[0], detail[1], bool(detail[2]))
        out += "```"
        await ctx.send(out)

    @perms.command(name="all", hidden=True, description="Display permission rules for all guilds")
    @dev_check()
    async def _p_all(self, ctx):
        """Displays all permissions rules, in all guilds Talos is in."""
        result = self.database.get_all_perm_rules()
        if len(result) == 0:
            await ctx.send("All permissions default")
            return
        guild_perms = {}
        for line in result:
            if guild_perms.get(line[0], None) is None:
                guild_perms[line[0]] = {}
            if guild_perms.get(line[0]).get(line[1], None) is None:
                guild_perms[line[0]][line[1]] = {}
            if guild_perms.get(line[0]).get(line[1]).get(line[2], None) is None:
                guild_perms[line[0]][line[1]][line[2]] = []
            guild_perms[line[0]][line[1]][line[2]].append([line[3], line[4], line[5]])

        out = "```"
        for guild in guild_perms:
            guild_name = self.bot.get_guild(guild)
            out += "Guild: {}\n".format(guild_name)
            for command in guild_perms[guild]:
                out += "    Command: {}\n".format(command)
                for level in sorted(guild_perms[guild][command], key=lambda a: self.LEVELS[a]):
                    out += "        Level: {}\n".format(level)
                    if level == "guild":
                        out += "            {}\n".format(guild_perms[guild][command][level])
                    else:
                        for detail in guild_perms[guild][command][level]:
                            out += "            {1}-{0}: {2}\n".format(detail[0], detail[1], bool(detail[2]))
        out += "```"
        await ctx.send(out)

    @commands.group(description="Options related commands")
    async def options(self, ctx):
        """Command to change Talos guild options. All of these only effect the current guild. Check """\
            """`^help options list` for a list of available options, and what they do."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'set', 'list', and 'default'.")

    @options.command(name="set", description="Set guild options")
    @commands.guild_only()
    async def _opt_set(self, ctx, option, value):
        """Set an option. Most options are true or false. See `^help options list` for available options"""
        try:
            option_type = self.database.get_column_type("guild_options", option)
        except ValueError:
            await ctx.send("Eh eh eh, letters and numbers only.")
            return
        if option_type == "tinyint":
            if value.upper() == "ALLOW" or value.upper() == "TRUE":
                value = True
            elif value.upper() == "FORBID" or value.upper() == "FALSE":
                value = False
            else:
                await ctx.send("Sorry, that option only accepts true or false values.")
                return
        if option_type == "varchar":
            value = re.sub(r"(?<!\\)\\((?:\\\\)*)s", space_replace, value)
            value = re.sub(r"\\\\", r"\\", value)
        if option_type is not None:
            self.database.set_guild_option(ctx.guild.id, option, value)
            await ctx.send("Option {} set to `{}`".format(option, value))
        else:
            await ctx.send("I don't recognize that option.")

    @options.command(name="list", description="Display guild options")
    @commands.guild_only()
    async def _opt_list(self, ctx):
        """Displays list of what options are currently set to in this guild. Available options are:
        rich_embeds: whether Talos will use any embedded messages in this guild.
        fail_message: whether Talos will post a message for unknown commands
        pm_help: whether Talos will PM help or post it in the channel
        commands: whether the Commands cog is active in this guild
        user_commands: whether the UserCommands cog is active in this guild
        joke_commands: whether the JokeCommands cog is active in this guild
        writing_prompts: whether to post daily writing prompts
        prompts_channel: the name of the channel to post daily prompts to, if above option is true
        prefix: command prefix for Talos to use in this guild. @ mention will always work"""
        out = "```"
        name_types = self.database.get_columns("guild_options")
        options = self.database.get_guild_options(ctx.guild.id)
        for index in range(len(options)):
            if options[index] == ctx.guild.id or options[index] == -1:
                continue
            option = options[index] if name_types[index][1] == "varchar" else bool(options[index])
            out += "{}: {}\n".format(name_types[index][0], option)
        out += "```"
        if out == "``````":
            await ctx.send("No options available.")
            return
        await ctx.send(out)

    @options.command(name="default", description="Set guild option to default")
    @commands.guild_only()
    async def _opt_default(self, ctx, option):
        """Sets an option to its default value, as in a guild Talos had just joined."""
        try:
            data_type = self.database.get_column_type("guild_options", option)
        except ValueError:
            await ctx.send("Eh eh eh, letters and numbers only.")
            return
        if data_type is not None:
            self.database.remove_guild_option(ctx.guild.id, option)
            await ctx.send("Option {} set to default".format(option))
        else:
            await ctx.send("I don't recognize that option.")

    @options.command(name="all", hidden=True, description="Display all guild options")
    @dev_check()
    async def _opt_all(self, ctx):
        """Displays all guild options in every guild Talos is in. Condensed to save your screen."""
        all_options = self.database.get_all_guild_options()
        name_types = self.database.get_columns("guild_options")
        out = "```"
        for options in all_options:
            for index in range(len(options)):
                key = options[index]
                if self.bot.get_guild(key) or key == -1:
                    out += "Guild: {}\n".format(self.bot.get_guild(key))
                    continue
                if key is None:
                    continue
                option = key if name_types[index][1] == "varchar" else bool(key)
                out += "    {}: {}\n".format(name_types[index][0], option)
        out += "```"
        if out == "``````":
            await ctx.send("No options available.")
            return
        await ctx.send(out)


def setup(bot):
    bot.add_cog(AdminCommands(bot))
