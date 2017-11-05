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
def op_check():
    """Determine whether the person calling the command is an operator or admin."""
    def predicate(ctx):

        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            return True
        command = str(ctx.command)

        if str(ctx.author) in ADMINS or\
           len(ctx.bot.get_ops(ctx.guild.id)) == 0 and ctx.author.guild_permissions.administrator or\
           ctx.author == ctx.guild.owner or\
           str(ctx.author) in ctx.bot.get_ops(ctx.guild.id):
            return True

        perms = ctx.bot.get_perm_rules(ctx.guild.id, command)
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
    If no ops exist, anyone with admin role permission can use op commands"""

    __slots__ = ['bot']

    LEVELS = {"guild": 0, "channel": 1, "role": 2, "user": 3}

    def __init__(self, bot):
        """Initializes the AdminCommands cog. Takes an instance of Talos to use while running."""
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
        """Verifies Talos data, making sure that all existing guilds have proper data and non-existent guilds don't"""\
            """ have data."""
        added, removed = await self.bot.verify()
        await ctx.send("Data Verified. {} objects added, {} objects removed.".format(added, removed))

    @commands.command(hidden=True)
    @admin_check()
    async def eval(self, ctx, *text):
        """Evaluate a given string as python code. Prints the return, if not empty."""
        program = ' '.join(text)
        try:
            result = str(eval(program))
            if result is not None and result is not "":
                result = re.sub(r"([\\_*~])", r"\\\g<1>", result)
                await ctx.send(result)
        except Exception as e:
            await ctx.send("Program failed with {}: {}".format(e.__class__.__name__, e))

    @commands.command(hidden=True)
    @admin_check()
    async def exec(self, ctx, *text):
        """Execute a given string as python code. replaces ';' with newlines and \t with tabs, for multiline."""
        program = ' '.join(text)
        program = re.sub(r"(?<!\\)((?:\\\\)*);", "\n", program)
        program = re.sub(r"(?<!\\)\\((?:\\\\)*)t", "\t", program)
        try:
            exec(program)
        except Exception as e:
            await ctx.send("Program failed with {}: {}".format(e.__class__.__name__, e))

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
        if str(member) not in ctx.bot.get_ops(ctx.guild.id):
            ctx.bot.add_op(ctx.guild.id, str(member))
            await ctx.send("Opped {0.name}!".format(member))
        else:
            await ctx.send("That user is already an op!")

    @ops.command(name="remove")
    @commands.guild_only()
    async def _ops_remove(self, ctx, member):
        """Removes an operator user"""
        member_object = discord.utils.find(lambda x: x.name == member or str(x) == member, ctx.guild.members)
        if member_object is not None:
            member = member_object
        if str(member) in ctx.bot.get_ops(ctx.guild.id):
            ctx.bot.remove_op(ctx.guild.id, str(member))
            if isinstance(member, discord.Member):
                await ctx.send("De-opped {0.name}".format(member))
            else:
                await ctx.send("De-opped invalid user")
        else:
            await ctx.send("That person isn't an op!")

    @ops.command(name="list")
    @commands.guild_only()
    async def _ops_list(self, ctx):
        """Displays all operators for the current server"""
        opslist = ctx.bot.get_ops(ctx.guild.id)
        if len(opslist) > 0:
            out = "```"
            for op in opslist:
                out += "{}\n".format(op)
            out += "```"
            await ctx.send(out)
        else:
            await ctx.send("This server currently has no operators.")

    @ops.command(name="all", hidden=True)
    @admin_check()
    async def _ops_all(self, ctx):
        """Displays all operators everywhere"""
        all_ops = ctx.bot.get_all_ops()
        consumed = []
        out = "```"
        for key in all_ops:
            if key[0] not in consumed:
                out += "Server: {}\n".format(self.bot.get_guild(key[0]))
                consumed.append(key[0])
            out += "    {}\n".format(key[1])
        if out != "```":
            out += "```"
            await ctx.send(out)
        else:
            await ctx.send("No ops currently")

    @commands.group()
    @op_check()
    async def perms(self, ctx):
        """Permissions related commands. Talos permissions are divided into 4 levels, with each level having a"""\
           """ default priority. The levels, in order from lowest to highest default priority, are:
           -Guild
           -Channel
           -Role
           -User
           If one doesn't like the default priority, it can be changed by adding a number to the end of the command."""\
           """ Priority defaults are 10 for guild, then going up by ten for each level, ending with User being 40.
           One can 'allow' or 'forbid' specifics at each level, or simply 'allow' or 'forbid' the whole guild."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'create', 'list', and 'remove'.")

    @perms.command(name="create")
    @commands.guild_only()
    async def _p_create(self, ctx, command: str, level: str, allow: str, name: str=None, priority: str=None):
        """Create or alter a permissions rule. Provide a command, one of the four levels, whether to allow or """\
            """forbid, if the level isn't guild then a name, and a priority if you don't want default."""
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
            self.bot.set_perm_rule(ctx.guild.id, command, level, allow, priority, name)
            await ctx.send("Permissions for command **{}** at level **{}** updated.".format(command, level))
        elif command not in self.bot.all_commands:
            await ctx.send("I don't recognize that command, so I can't set permissions for it!")
        else:
            await ctx.send("Unrecognized permission level.")

    @perms.command(name="remove")
    @commands.guild_only()
    async def _p_remove(self, ctx, *args):
        """Remove a permissions rule or set of rules."""
        if len(args) > 0:
            command = args[0]
        else:
            command = None
        if len(args) > 1:
            level = args[1]
            level = level.lower()
        else:
            level = None
        if level in self.LEVELS or level is None:
            target = None
            if len(args) > 2:
                if level == "user":
                    target = str(discord.utils.find(lambda u: u.name == args[2], ctx.guild.members))
                elif level == "role":
                    target = str(discord.utils.find(lambda r: r.name == args[2], ctx.guild.roles))
                elif level == "channel":
                    target = str(discord.utils.find(lambda c: c.name == args[2], ctx.guild.channels))

            self.bot.remove_perm_rules(ctx.guild.id, command, level, target)
            if command is None:
                await ctx.send("Permissions for guild cleared")
                return
            if level is None:
                await ctx.send("Permissions for command **{}** at all levels cleared.".format(command))
                return
            if target is None:
                await ctx.send("Permissions for command **{}** at level **{}** cleared.".format(command, level))
                return
            out = "Permissions for command **{}** at level **{}** for **{}** cleared.".format(command, level, target)
            await ctx.send(out)
        else:
            await ctx.send("Unrecognized permission level.")

    @perms.command(name="list")
    @commands.guild_only()
    async def _p_list(self, ctx):
        """Lists permissions rules for the current guild"""
        result = self.bot.get_perm_rules(ctx.guild.id)
        if len(result) == 0:
            await ctx.send("No permissions set for this server.")
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

    @perms.command(name="all", hidden=True)
    @admin_check()
    async def _p_all(self, ctx):
        """Displays all permissions everywhere"""
        result = self.bot.get_all_perm_rules()
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
        try:
            option_type = self.bot.get_column_type("guild_options", option)
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
            ctx.bot.set_guild_option(ctx.guild.id, option, value)
            await ctx.send("Option {} set to `{}`".format(option, value))
        else:
            await ctx.send("I don't recognize that option.")

    @options.command(name="list")
    @commands.guild_only()
    async def _opt_list(self, ctx):
        """List of what options are currently set on the server. Do `^help options [option name]` for details on"""\
            """ an individual option"""
        out = "```"
        name_types = self.bot.get_columns("guild_options")
        options = self.bot.get_guild_options(ctx.guild.id)
        for index in range(len(options)):
            if options[index] == ctx.guild.id or options[index] == -1:
                continue
            option = options[index] if name_types[index][1] == "varchar" else bool(options[index])
            out += "{}: {}\n".format(name_types[index][0], option)
        out += "```"
        await ctx.send(out)

    @options.command(name="default")
    @commands.guild_only()
    @op_check()
    async def _opt_default(self, ctx, option):
        """Sets an option to its default value, as in a server Talos had just joined."""
        try:
            data_type = self.bot.get_column_type("guild_options", option)
        except ValueError:
            await ctx.send("Eh eh eh, letters and numbers only.")
            return
        if data_type is not None:
            ctx.bot.set_guild_option(ctx.guild.id, option, None)
            await ctx.send("Option {} set to default".format(option))
        else:
            await ctx.send("I don't recognize that option.")

    @options.command(name="all", hidden=True)
    @admin_check()
    async def _opt_all(self, ctx):
        """Displays all options everywhere"""
        all_options = self.bot.get_all_guild_options()
        name_types = self.bot.get_columns("guild_options")
        out = "```"
        for options in all_options:
            for index in range(len(options)):
                key = options[index]
                if self.bot.get_guild(key) or key == -1:
                    out += "Server: {}\n".format(self.bot.get_guild(key))
                    continue
                if key is None:
                    continue
                option = key if name_types[index][1] == "varchar" else bool(key)
                out += "    {}: {}\n".format(name_types[index][0], option)
        out += "```"
        await ctx.send(out)


def setup(bot):
    bot.add_cog(AdminCommands(bot))
