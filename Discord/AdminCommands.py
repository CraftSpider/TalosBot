"""
    Admin Commands cog for Talos.
    Holds all commands relevant to administrator function, be it server specific or all of Talos.

    Author: CraftSpider
"""
import discord
import logging
import random
import string
import asyncio
import datetime
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
perms = defaultdict(lambda: {})
# Security keys, for security-locked commands.
secure_keys = defaultdict(lambda: "")

# Configure Logging
logging.basicConfig(level=logging.INFO)


def key_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """Generates random strings for things that need keys. Allows variable size and character lists, if desired."""
    return ''.join(random.choice(chars) for _ in range(size))


def set_perm(guild, command, level, name, allow):
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


def remove_perm(guild, command, level, name):
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
    elif command is not None:
        del perms[guild][command]
    else:
        del perms[guild]


#
# Admin Command Checks
#
def admin_check():
    """Determine whether the person calling the command is an operator or admin."""
    def predicate(ctx):
        guild_id = str(ctx.guild.id)
        command = str(ctx.command)

        if str(ctx.author) in ADMINS or\
           len(ops[guild_id]) == 0 and ctx.author.guild_permissions.administrator or\
           ctx.author == ctx.guild.owner or\
           str(ctx.author) in ops[guild_id]:
            return True

        if guild_id not in perms.keys():
            return False
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
    If no Ops exist, anyone with admin can use op commands"""

    __slots__ = ['bot']

    LEVELS = ["guild", "channel", "role", "user"]
    LEVELS_DICT = {"guild": 0, "channel": 1, "role": 2, "user": 3}

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
        if len(text) is not 0:
            await ctx.send(" ".join(text))

    @commands.command(usage="[number=10]")
    @admin_check()
    async def purge(self, ctx, number: str="10", *key):
        """Purges messages from a channel. By default, this will be 10 (including the invoking command)."""\
            """ Use 'all' to purge whole channel."""
        if number != "all":
            number = int(number)
            if number > 100 and (len(key) == 0 or key[0] != secure_keys[str(ctx.guild.id)]):
                rand_key = key_generator()
                secure_keys[str(ctx.guild.id)] = rand_key
                await ctx.send("Are you sure? If so, re-invoke with {} on the end.".format(rand_key))
            else:
                async for message in ctx.history(limit=number):
                    await message.delete()
                    await asyncio.sleep(.5)
        else:
            if len(key) == 0 or key[0] != secure_keys[str(ctx.guild.id)]:
                rand_key = key_generator()
                secure_keys[str(ctx.guild.id)] = rand_key
                await ctx.send("Are you sure? If so, re-invoke with {} on the end.".format(rand_key))
            elif key[0] == secure_keys[str(ctx.guild.id)]:
                async for message in ctx.history(limit=None):
                    await message.delete()
                    await asyncio.sleep(.5)
                secure_keys[str(ctx.guild.id)] = ""

    @commands.command()
    @admin_check()
    async def talos_perms(self, ctx):
        """Has Talos print out their current guild permissions"""
        perms = ctx.me.guild_permissions
        out = "```Guild Permissions:\n"
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
        await self.bot.change_presence(game=discord.Game(name=game, type=0))
        await ctx.send("Now playing {}".format(game))

    @commands.command(hidden=True)
    @admin_only()
    async def streaming(self, ctx, *streaming: str):
        """Changes the game Talos is streaming"""
        game = " ".join(map(str, streaming))
        await self.bot.change_presence(game=discord.Game(name=game, type=1))
        await ctx.send("Now streaming {}".format(game))

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
    @admin_check()
    async def embed(self, ctx):
        """Testing with embeds"""
        logging.info("Posting embed")
        embed = discord.Embed(title="Productivity War", colour=ctx.author.colour,
                              description="CraftSpider won the PW!",
                              timestamp=datetime.datetime.now())
        embed.add_field(name="Start", value="Sep 24 - 22:41:33", inline=True)
        embed.add_field(name="End", value="Sep 24 - 22:41:37", inline=True)
        embed.add_field(name="Total", value="00:00:04")
        embed.add_field(name="Times", value="CraftSpider#0269 - 0:00:04\nhiddenstorys#3600 - 0:00:02")
        # embed.set_footer(icon_url=ctx.author.avatar_url, text=ctx.author.display_name)
        await ctx.send(embed=embed)

    @commands.group()
    @admin_check()
    async def ops(self, ctx):
        """Operator related commands. By default, anyone on a server with admin privileges is an Op."""\
            """ Adding someone to the list will override this behavior.
            The Server Owner is also always Op, and this behavior can't be overridden for security reasons."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'add', 'list', and 'remove'.")

    @ops.command(name="add")
    async def _o_add(self, ctx, member: discord.Member):
        """Adds a new operator user"""
        if str(member) not in ops[str(ctx.guild.id)]:
            ops[str(ctx.guild.id)].append(str(member))
            await ctx.send("Opped {0.name}!".format(member))
            await self.bot.save()
        else:
            await ctx.send("That user is already an op!")

    @ops.command(name="remove")
    async def _o_remove(self, ctx, member: discord.Member):
        """Removes an operator user"""
        try:
            ops[str(ctx.guild.id)].remove(str(member))
            await ctx.send("De-opped {0.name}".format(member))
            await self.bot.save()
        except ValueError:
            await ctx.send("That person isn't an op!")

    @ops.command(name="list")
    async def _o_list(self, ctx):
        """Displays all operators for the current server"""
        if ops[str(ctx.guild.id)]:
            out = "```"
            for op in ops[str(ctx.guild.id)]:
                out += "{}\n".format(op)
            out += "```"
            await ctx.send(out)
        else:
            await ctx.send("This server currently has no operators.")

    @ops.command(hidden=True, name="all")
    @admin_only()
    async def _o_all(self, ctx):
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
    @admin_check()
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
    async def _p_create(self, ctx, command: str, level: str, *options):
        """Create or alter a permissions rule"""
        level = level.lower()
        if command in self.bot.all_commands and level in self.LEVELS:
            if len(options) < 2 and level != "guild":
                await ctx.send("You need to include both a name and either 'allow' or 'forbid'")
                return
            elif len(options) < 1:
                await ctx.send("You need to include an 'allow' or 'forbid'")
                return

            if level == "user":
                spec = discord.utils.find(lambda u: u.name == options[0], ctx.guild.members)
                if spec is None:
                    await ctx.send("Sorry, I couldn't find the user {}!".format(options[0]))
                    return
                spec = str(spec)
            elif level == "role":
                spec = discord.utils.find(lambda r: r.name == options[0], ctx.guild.roles)
                if spec is None:
                    await ctx.send("Sorry, I couldn't find the role {}!".format(options[0]))
                    return
                spec = str(spec)
            elif level == "channel":
                spec = discord.utils.find(lambda c: c.name == options[0], ctx.guild.channels)
                if spec is None:
                    await ctx.send("Sorry, I couldn't find the channel {}!".format(options[0]))
                    return
                spec = str(spec)
            else:
                spec = None

            if "allow" in options:
                set_perm(str(ctx.guild.id), command, level, spec, True)
            elif "forbid" in options:
                set_perm(str(ctx.guild.id), command, level, spec, False)
            else:
                await ctx.send("I don't recognize any options I can change in that.")
                return
            await self.bot.update_perms()
            await ctx.send("Permissions for command **{}** at level **{}** updated.".format(command, level))
        elif command not in self.bot.all_commands:
            await ctx.send("I don't recognize that command, so I can't set permissions for it!")
        else:
            await ctx.send("Unrecognized permission level.")

    @perms.command(name="remove")
    async def _p_remove(self, ctx, command: str, *options):
        """Remove a permissions rule or set of rules."""
        if len(options) > 0:
            level = options[0]
            level = level.lower()
        else:
            level = None
        if command in self.bot.all_commands and (level in self.LEVELS or level is None):
            if len(options) > 1:
                if level == "user":
                    spec = str(discord.utils.find(lambda u: u.name == options[1], ctx.guild.members))
                elif level == "role":
                    spec = str(discord.utils.find(lambda r: r.name == options[1], ctx.guild.roles))
                elif level == "channel":
                    spec = str(discord.utils.find(lambda c: c.name == options[1], ctx.guild.channels))
                else:
                    spec = None
            else:
                spec = None

            remove_perm(str(ctx.guild.id), command, level, spec)
            await self.bot.update_perms()
            if level is None:
                await ctx.send("Permissions for command **{}** at all levels cleared.".format(command))
                return
            await ctx.send("Permissions for command **{}** at level **{}** cleared.".format(command, level))
        elif command not in self.bot.commands:
            await ctx.send("I don't recognize that command, so I can't clear permissions for it!")
        else:
            await ctx.send("Unrecognized permission level.")

    @perms.command(name="list")
    async def _p_list(self, ctx):
        """List current permissions rules"""
        serv_perms = perms[str(ctx.guild.id)]
        if len(serv_perms) == 0:
            await ctx.send("No permissions set for this server.")
            return
        out = "```"
        for command in serv_perms:
            out += "Command: {}\n".format(command)
            for level in sorted(serv_perms[command], key=lambda a: self.LEVELS_DICT[a]):
                out += "    Level: {}\n".format(level)
                if level == "guild":
                    out += "        {}\n".format(serv_perms[command][level])
                else:
                    for spec in serv_perms[command][level]:
                        out += "        {}: {}\n".format(spec, serv_perms[command][level][spec])
        out += "```"
        await ctx.send(out)

    @perms.command(name="all")
    @admin_only()
    async def _p_all(self, ctx):
        await ctx.send("`{}`".format(perms))


def setup(bot):
    bot.add_cog(AdminCommands(bot))
