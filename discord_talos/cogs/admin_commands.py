"""
    Admin Commands cog for Talos.
    Holds all commands relevant to administrator function, guild specific stuff.

    Author: CraftSpider
"""
import asyncio
import discord
import logging
import random
import string
import re
import utils
import utils.dutils as dutils
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


#
# Admin Command Checks
#
def admin_check(self, ctx):
    """Determine whether the person calling the command is an admin or dev."""
    if isinstance(ctx.channel, discord.abc.PrivateChannel):
        return True
    command = str(ctx.command)

    if ctx.author.id in self.bot.DEVS:
        return True

    admins = self.database.get_admins(ctx.guild.id)
    if len(admins) == 0 and ctx.author.guild_permissions.administrator or\
       ctx.author == ctx.guild.owner or\
       next((x for x in admins if x.user_id == ctx.guild.id), None) is not None:
        return True

    perms = self.database.get_perm_rules(ctx.guild.id, command)
    if len(perms) == 0:
        return False
    perms.sort()
    for perm in perms:
        result = perm.get_allowed(ctx)
        if result is None:
            continue
        return result
    return False


def dev_check():
    """Determine whether the person calling the command is a dev."""
    def predicate(ctx):
        return ctx.author.id in ctx.bot.DEVS
    return commands.check(predicate)


#
# Admin Cog Class
#
class AdminCommands(dutils.TalosCog):
    """These commands can only be used by Admins or Devs, and will work at any time.
    If no admins list is set, anyone with administrator role permission can use admin commands"""

    LEVELS = {"guild": 0, "channel": 1, "role": 2, "user": 3}
    __local_check = admin_check

    @commands.command(description="Changes Talos' nickname")
    @commands.guild_only()
    async def nick(self, ctx, *, nickname):
        """Sets Talos' nickname in the current guild."""
        if len(nickname) > 32:
            await ctx.send("Nickname must be 32 characters or fewer")
            return
        await ctx.me.edit(nick=nickname)
        await ctx.send(f"Nickname changed to {nickname}")

    @commands.command(description="Makes Talos repeat you")
    async def repeat(self, ctx, *, text):
        """Causes Talos to repeat whatever you just said, exactly."""
        await ctx.send(text)

    @commands.command(usage="[number=10]", description="Remove messages from a channel")
    @commands.guild_only()
    async def purge(self, ctx, number="10", key=None):
        """Purges messages from a channel. By default, this will be 10 (including the invoking command)."""\
            """ Use 'all' to purge whole channel. Confirmation keys should be tacked on the end, so """\
            """`^purge 100 [key]`"""
        if number != "all":
            number = int(number)
            if number >= 100 and (key is None or key != secure_keys[str(ctx.guild.id)]):
                rand_key = key_generator()
                secure_keys[str(ctx.guild.id)] = rand_key
                await ctx.send(f"Are you sure? If so, re-invoke with {rand_key} on the end.")
            else:
                await ctx.channel.purge(limit=number)
        else:
            if len(key) == 0 or key[0] != secure_keys[str(ctx.guild.id)]:
                rand_key = key_generator()
                secure_keys[str(ctx.guild.id)] = rand_key
                await ctx.send(f"Are you sure? If so, re-invoke with {rand_key} on the end.")
            elif key[0] == secure_keys[str(ctx.guild.id)]:
                await ctx.channel.purge(limit=None)
                secure_keys[str(ctx.guild.id)] = ""

    @commands.command(description="Kick a user from chat")
    @commands.guild_only()
    async def kick(self, ctx, user: discord.Member, reason="Kicked from guild by Talos"):
        """Kicks a given user from the current guild. Only accepts a user who is currently in the guild"""
        await user.kick(reason=reason)
        await self.bot.mod_log(ctx, "kick", user, reason)
        await ctx.send(f"User {user} kicked")

    @commands.command(description="Ban a user from chat")
    @commands.guild_only()
    async def ban(self, ctx, user: discord.Member, reason="Banned from guild by Talos"):
        """Bans a given user from the current guild. Currently only accepts a user who is currently in the guild"""
        await user.ban(reason=reason)
        await self.bot.mod_log(ctx, "ban", user, reason)
        await ctx.send(f"User {user} banned")

    @commands.command(aliases=["mute"], description="Silence a user")
    @commands.guild_only()
    async def silence(self, ctx, user: discord.Member, length=None, reason="Silenced by Talos"):
        """Silences a user, optionally takes in a length of time and a reason for silencing. A role called 'Muted' """\
            """or 'Silenced' with the necessary permissions in place must exist for this to work."""
        muted = list(filter(lambda x: x.name.lower() == "muted" or x.name.lower() == "silenced", ctx.guild.roles))
        if not muted:
            await ctx.send("No Muted or Silenced role")
            return
        role = muted[0]
        await user.add_roles(role, reason=reason)
        await self.bot.mod_log(ctx, "silence", user, reason)
        await ctx.send(f"User {user} silenced")
        if length is not None:
            if isinstance(length, str):
                period = utils.data.EventPeriod(length)
            elif isinstance(length, int):
                period = utils.data.EventPeriod("")
                period.minutes = length

            async def unmuter():
                await asyncio.sleep(int(period))
                await user.remove_roles(role, reason="Silence timer up")

            self.bot.loop.create_task(unmuter())

    @commands.command(description="Display current Talos perms")
    @commands.guild_only()
    async def talos_perms(self, ctx):
        """Has Talos display their current effective guild permissions. This is channel independent, """\
            """channel-specific perms aren't taken into account."""
        out = "```Guild Permissions:\n"
        out += ', '.join(map(lambda x: x[0], filter(lambda y: y[1] is True, ctx.me.guild_permissions)))
        out += "```"
        await ctx.send(out)

    @commands.group(description="Admin related commands")
    async def admins(self, ctx):
        """By default, anyone on a guild with administrator privileges is an Admin. Adding someone to the list will """\
            """ override this behavior.
            The Guild Owner is also always Admin, and this behavior can't be overridden for security reasons."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'add', 'list', and 'remove'.")

    @admins.command(name="add", description="Adds a new admin")
    @commands.guild_only()
    async def _ad_add(self, ctx, member: discord.Member):
        """Adds a user to the guild admin list."""
        new_admin = utils.TalosAdmin((ctx.guild.id, member.id))
        if new_admin not in self.database.get_admins(ctx.guild.id):
            self.database.save_item(new_admin)
            await ctx.send(f"Added admin {member.name}!")
        else:
            await ctx.send("That user is already an admin!")

    @admins.command(name="remove", description="Removes an admin")
    @commands.guild_only()
    async def _ad_remove(self, ctx, member):
        """Removes an admin user from the guild list"""
        member_object = discord.utils.find(
            lambda x: x.name == member or str(x) == member or (member.isnumeric() and x.id == int(member)),
            ctx.guild.members
        )
        if member_object is not None:
            member = member_object.id
        elif member.isnumeric():
            member = int(member)

        admin = list(filter(lambda x: x.user_id == member, self.database.get_admins(ctx.guild.id)))
        if admin:
            self.database.remove_item(admin[0])
            if member_object:
                await ctx.send(f"Removed admin from {member_object.name}")
            else:
                await ctx.send("Removed admin from invalid user")
        else:
            await ctx.send("That person isn't an admin!")

    @admins.command(name="list", description="Display admins")
    @commands.guild_only()
    async def _ad_list(self, ctx):
        """Displays all admins for the current guild"""
        admin_list = self.database.get_admins(ctx.guild.id)
        if len(admin_list) > 0:
            out = "```"
            for admin in admin_list:
                admin_name = self.bot.get_user(admin.user_id)
                admin_name = str(admin_name) if admin_name is not None else admin.user_id
                out += f"{admin_name}\n"
            out += "```"
            await ctx.send(out)
        else:
            await ctx.send("This guild currently has no administrators.")

    @admins.command(name="all", hidden=True, description="Display all admins")
    @dev_check()
    async def _ad_all(self, ctx):
        """Displays all admins in every guild Talos is in"""
        all_admins = self.database.get_all_admins()
        consumed = []
        out = "```"
        for admin in all_admins:
            if admin.guild_id not in consumed:
                out += f"Guild: {self.bot.get_guild(admin.guild_id)}\n"
                consumed.append(admin.guild_id)
            admin = self.bot.get_user(admin.user_id)
            admin = str(admin) if admin is not None else admin.user_id
            out += f"    {admin}\n"
        if out != "```":
            out += "```"
            await ctx.send(out)
        else:
            await ctx.send("No admins currently")

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

    @perms.command(name="add", aliases=["create"], description="Create or alter permission rules")
    @commands.guild_only()
    async def _p_add(self, ctx, command, level, allow, name=None, priority: int=None):
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

        found = self.bot.find_command(command) is not None
        if found and level in self.LEVELS:
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
                await ctx.send(f"Sorry, I couldn't find the user {old_name}!")
                return

            name = str(name) if name != "" else "SELF"
            priority = priority or utils.sql.levels[level]

            perm_rule = utils.PermissionRule((ctx.guild.id, command, level, name, priority, allow))
            self.database.save_item(perm_rule)
            await ctx.send(f"Permissions for command **{command}** at level **{level}** updated.")
        elif not found:
            await ctx.send("I don't recognize that command, so I can't set permissions for it!")
        else:
            await ctx.send("Unrecognized permission level.")

    @perms.command(name="remove", aliases=["delete"], description="Remove permission rules")
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
            perm_rule = utils.PermissionRule((ctx.guild.id, command, level, name, None, None))
            self.database.remove_item(perm_rule, general=True)
            if command is None:
                await ctx.send("Permissions for guild cleared")
            elif level is None:
                await ctx.send(f"Permissions for command **{command}** at all levels cleared.")
            elif name is None:
                await ctx.send(f"Permissions for command **{command}** at level **{level}** cleared.")
            else:
                await ctx.send(f"Permissions for command **{command}** at level **{level}** for **{name}** cleared.")
        else:
            await ctx.send("Unrecognized permission level.")

    @perms.command(name="list", description="Display permission rules for the current guild")
    @commands.guild_only()
    async def _p_list(self, ctx):
        """Displays a list of all permissions rules for the current guild"""
        result = self.database.get_perm_rules(ctx.guild.id)
        if len(result) == 0:
            await ctx.send("No permissions set for this guild.")
            return
        guild_perms = {}
        for perm in result:
            if guild_perms.get(perm.command, None) is None:
                guild_perms[perm.command] = {}
            if guild_perms.get(perm.command).get(perm.perm_type, None) is None:
                guild_perms[perm.command][perm.perm_type] = []
            guild_perms[perm.command][perm.perm_type].append([perm.target, perm.priority, perm.allow])

        out = "```"
        for command in guild_perms:
            out += f"Command: {command}\n"
            for level in sorted(guild_perms[command], key=lambda a: self.LEVELS[a]):
                out += f"    Level: {level}\n"
                if level == "guild":
                    out += f"        {guild_perms[command][level]}\n"
                else:
                    for detail in guild_perms[command][level]:
                        out += f"        {detail[1]}-{detail[0]}: {bool(detail[2])}\n"
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
        for permission in result:
            if guild_perms.get(permission.id, None) is None:
                guild_perms[permission.id] = {}
            if guild_perms.get(permission.id).get(permission.command, None) is None:
                guild_perms[permission.id][permission.command] = {}
            if guild_perms.get(permission.id).get(permission.command).get(permission.perm_type, None) is None:
                guild_perms[permission.id][permission.command][permission.perm_type] = []
            guild_perms[permission.id][permission.command][permission.perm_type].append([permission.target,
                                                                                         permission.priority,
                                                                                         permission.allow])

        out = "```"
        for guild in guild_perms:
            guild_name = self.bot.get_guild(guild)
            out += f"Guild: {guild_name}\n"
            for command in guild_perms[guild]:
                out += f"    Command: {command}\n"
                for level in sorted(guild_perms[guild][command], key=lambda a: self.LEVELS[a]):
                    out += f"        Level: {level}\n"
                    if level == "guild":
                        out += f"            {guild_perms[guild][command][level]}\n"
                    else:
                        for detail in guild_perms[guild][command][level]:
                            out += f"            {detail[1]}-{detail[0]}: {bool(detail[2])}\n"
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
            guild_options = self.database.get_guild_options(ctx.guild.id)
            cur_val = getattr(guild_options, option)
            if isinstance(cur_val, (int, bool)):
                if value.upper() == "ALLOW" or value.upper() == "TRUE":
                    value = True
                elif value.upper() == "FORBID" or value.upper() == "FALSE":
                    value = False
                else:
                    await ctx.send("Sorry, that option only accepts true or false values.")
                    return
            if isinstance(cur_val, str):
                value = re.sub(r"(?<!\\)\\((?:\\\\)*)s", utils.space_replace, value)
                value = re.sub(r"\\\\", r"\\", value)
            setattr(guild_options, option, value)
            self.database.save_item(guild_options)
            await ctx.send(f"Option {option} set to `{value}`")
        except AttributeError:
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
        prefix: command prefix for Talos to use in this guild. @ mention will always work
        timezone: what timezone for Talos to use for displayed times, supports any timezone abbreviation"""
        out = "```"
        options = self.database.get_guild_options(ctx.guild.id)
        for item in options.__slots__[1:]:
            out += f"{item}: {getattr(options, item)}\n"
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
            guild_options = self.database.get_guild_options(ctx.guild.id)
            setattr(guild_options, option, None)
            self.database.save_item(guild_options)
            await ctx.send(f"Option {option} set to default")
        except AttributeError:
            await ctx.send("I don't recognize that option.")

    @options.command(name="all", hidden=True, description="Display all guild options")
    @dev_check()
    async def _opt_all(self, ctx):
        """Displays all guild options in every guild Talos is in. Condensed to save your screen."""
        all_options = self.database.get_all_guild_options()
        out = "```"
        for options in all_options:
            out += f"Guild: {self.bot.get_guild(options.id)}\n"
            for item in options.__slots__[1:]:
                option = getattr(options, item)
                if option is None:
                    continue
                out += f"    {item}: {option}\n"
        out += "```"
        if out == "``````":
            await ctx.send("No options available.")
            return
        await ctx.send(out)

    @commands.group(description="Custom commands, Yay!")
    async def command(self, ctx):
        """Command for managing guild-only commands. Create, edit, delete, or list commands. To see documentation """\
            """on how to write more complex commands, check out the talos website CommandLang page. **Currently in """\
            """development, please report bugs on the github or official server**"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'add', 'edit', 'remove', and 'list'")

    @command.command(name="add", aliases=["create"], description="Add new command")
    async def _c_add(self, ctx, name, *, text):
        """Creates a new guild only command, first word will be the name, and everything after will define the """\
            """command"""
        if name in self.bot.all_commands:
            await ctx.send("Talos already has that command, no overwriting allowed.")
            return
        elif self.database.get_guild_command(ctx.guild.id, name):
            await ctx.send("That command already exists. Maybe you meant to `edit` it instead?")
            return
        self.database.save_item(utils.GuildCommand((ctx.guild.id, name, text)))
        await ctx.send(f"Command {name} created")

    @command.command(name="edit", description="Edit existing command")
    async def _c_edit(self, ctx, name, *, text):
        """Edits an existing command. Same format as adding a command."""
        if not self.database.get_guild_command(ctx.guild.id, name):
            await ctx.send("That command doesn't exist. Maybe you meant to `add` it instead?")
            return
        self.database.save_item(utils.GuildCommand((ctx.guild.id, name, text)))
        await ctx.send(f"Command {name} successfully edited")

    @command.command(name="remove", description="Remove existing command")
    async def _c_remove(self, ctx, name):
        """Removes a command from the guild."""
        if self.database.get_guild_command(ctx.guild.id, name) is None:
            await ctx.send("That command doesn't exist, sorry.")
            return
        self.database.remove_item(utils.GuildCommand((ctx.guild.id, name, None)), True)
        await ctx.send(f"Command {name} successfully removed")

    @command.command(name="list", description="List existing commands")
    async def _c_list(self, ctx):
        """Lists commands in this guild"""
        command_list = self.database.get_guild_commands(ctx.guild.id)
        if len(command_list) is 0:
            await ctx.send("This server has no custom commands")
            return
        out = "```\nServer Commands:\n"
        for command in command_list:
            out += f"{command.name}: {command.text}\n"
        out += "```"
        await ctx.send(out)

    @commands.group(description="Custom events, on a timer")
    async def event(self, ctx):
        """Allows the creation of custom events to occur on a regular basis. See the CommandLang page on the """\
            """official website for details of the language used to define these events."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'add', 'edit', 'remove', and 'list'")

    @event.command(name="add", description="Add a custom event")
    async def _e_add(self, ctx, name, period, *, text):
        """Creates a new custom event. First word is identifier name, Second word is a period. Period is defined as """\
            """1h for once an hour, 10m for once every ten minutes, 7d for once every week. Minimum time period """\
            """is 10 minutes. One may user multiple specifiers, eg 1d7m"""
        if self.database.get_guild_event(ctx.guild.id, name):
            await ctx.send("That event already exists. Maybe you meant to `edit` it instead?")
            return
        event = utils.GuildEvent((ctx.guild.id, name, period, ctx.channel.id, text))
        self.database.save_item(event)
        await ctx.send(f"Event {name} created")

    @event.command(name="edit", description="Edit an existing event")
    async def _e_edit(self, ctx, name, *, text):
        """Edits an existing event, changing what text is displayed when the event runs."""
        event = self.database.get_guild_event(ctx.guild.id, name)
        if not event:
            await ctx.send("That event doesn't exist. Maybe you meant to `add` it instead?")
            return
        event.name = name
        event.text = text
        self.database.save_item(event)
        await ctx.send(f"Event {name} successfully edited")

    @event.command(name="remove", description="Remove an event")
    async def _e_remove(self, ctx, name):
        """Delete an existing event, so it will no longer occur."""
        if self.database.get_guild_event(ctx.guild.id, name) is None:
            await ctx.send("That event doesn't exist, sorry.")
            return
        event = utils.GuildEvent((ctx.guild.id, name, None, None, None, None))
        self.database.remove_item(event, True)
        await ctx.send(f"Event {name} successfully removed")

    @event.command(name="list", description="List all events")
    async def _e_list(self, ctx):
        """Display a list of all events currently defined for this guild."""
        event_list = self.database.get_guild_events(ctx.guild.id)
        if len(event_list) is 0:
            await ctx.send("This server has no custom events")
            return
        out = "```\nServer Events:\n"
        for event in event_list:
            out += f"{event.name} - {event.period}: {event.text}\n"
        out += "```"
        await ctx.send(out)

    @commands.group(description="Retrieve a quote from the database", invoke_without_command=True)
    async def quote(self, ctx, author=None, *, quote=None):
        """Quote the best lines from chat for posterity"""
        if author is None:
            quote = self.database.get_random_quote(ctx.guild.id)
            if quote is None:
                await ctx.send("There are no quotes available for this guild")
                return
        else:
            try:
                author = int(author)
                quote = self.database.get_quote(ctx.guild.id, author)
                if quote is None:
                    await ctx.send(f"No quote for ID {author}")
                    return
            except ValueError:
                if quote is None:
                    await ctx.send("Quote ID must be a whole number.")
                    return
                command = self.bot.find_command("quote add")
                if await command.can_run(ctx):
                    await ctx.invoke(command, author, quote=quote)
                else:
                    await ctx.send("You don't have permission to do that, sorry")
                return

        if self.bot.should_embed(ctx):
            with dutils.PaginatedEmbed() as embed:
                embed.set_author(name=quote.author)
                embed.description = quote.quote
                embed.set_footer(text=f"#{quote.id}")
            for e in embed:
                await ctx.send(embed=e)
        else:
            await ctx.send(f"{quote.author}: \"{quote.quote}\" ({quote.id})")

    @quote.command(name="add", aliases=["create"], description="Add a new quote to the list")
    async def _q_add(self, ctx, author, *, quote):
        """Adds a new quote to this guild's list of quotes"""
        quote = utils.Quote([ctx.guild.id, None, author, quote])
        self.database.save_item(quote)
        await ctx.send(f"Quote from {author} added!")

    @quote.command(name="remove", description="Remove a quote")
    async def _q_remove(self, ctx, num: int):
        """Remove the quote with a specific ID"""
        quote = self.database.get_quote(ctx.guild.id, num)
        if quote is not None:
            self.database.remove_item(utils.Quote([ctx.guild.id, num, None, None]), True)
            await ctx.send(f"Removed quote {num}")
        else:
            await ctx.send(f"No quote for ID {num}")


def setup(bot):
    bot.add_cog(AdminCommands(bot))
