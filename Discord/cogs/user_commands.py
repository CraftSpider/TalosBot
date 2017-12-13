"""
    User Commands cog for Talos
    Holds all user specific commands, those things that alter a user's permissions, roles,
    Talos' knowledge of them, so on.

    Author: CraftSpider
"""
import discord
import logging
import asyncio
import utils
import re
from discord.ext import commands

logging = logging.getLogger("talos.user")


def space_replace(match):
    print(match.group(1))
    if match.group(1):
        return "\\"*int(len(match.group(0)) / 2) + " "
    else:
        return " "


class UserCommands(utils.TalosCog):
    """These commands can be used by anyone, as long as Talos is awake.\n"""\
        """The effects will apply to the person using the command."""

    @commands.command(signature="color <hex-code>", description="Set your role color")
    @commands.guild_only()
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

    @commands.command(description="Display current guild perms")
    @commands.guild_only()
    async def my_perms(self, ctx):
        """Has Talos display your current effective guild permissions. This is channel independent, channel-specific"""\
            """ perms aren't taken into account."""
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

    @commands.command(description="User registration command")
    async def register(self, ctx):
        """Registers you as a user with Talos. This creates a profile and options for you, and allows Talos to """\
            """save info."""
        if not self.database.get_user(ctx.author.id):
            self.database.register_user(ctx.author.id)
            await ctx.send("Registered new user!")
        else:
            await ctx.send("You're already a registered user.")

    @commands.command(description="User deletion command")
    async def deregister(self, ctx):
        """Deregisters you from Talos. All collected data is wiped, no account info will be saved until """\
            """you re-register."""
        if self.database.get_user(ctx.author.id):
            self.database.deregister_user(ctx.author.id)
            await ctx.send("Deregistered user")
        else:
            raise utils.NotRegistered(ctx.author)

    @commands.command(description="Display a user profile")
    async def profile(self, ctx, user: discord.User=None):
        """Displays you or another user's profile, if it exists. Defaults to your own profile, but accepts the name """\
            """of a user to display instead."""
        if user is None:
            user = ctx.author
        profile = self.database.get_user(user.id)
        if not profile:
            raise utils.NotRegistered(user)
        total_commands = profile[2]
        favorite_command = self.database.get_favorite_command(user.id)
        if self.bot.should_embed(ctx):
            embed = discord.Embed(title=profile[3] if profile[3] else False,
                                  description=profile[1] if profile[1] else "User has not set a description")
            embed.set_author(name=user.name, icon_url=user.avatar_url)
            value = "Total Invoked Commands: {0}\nFavorite Command: `{1[0]}`, invoked {1[1]} times.".format(
                total_commands, favorite_command
            )
            embed.add_field(name="Command Stats", value=value)
            await ctx.send(embed=embed)
        else:
            out = "```md\n"
            out += "{}\n".format(user.name)
            out += "{}\n".format(profile[1] if profile[1] else "User has not set a description")
            out += "# Command Stats:\n"
            out += "-  Total Invoked: {}\n".format(total_commands)
            out += "-  Favorite Command: {0[0]}, invoked {0[1]} times.".format(favorite_command)
            out += "```"
            await ctx.send(out)

    @commands.group(description="For checking or setting your own profile")
    async def user(self, ctx):
        """Options will show current user options, stats will display what Talos has saved about you, description """\
            """will set your user description, set will set user options, and remove will clear user options."""
        if not self.database.get_user(ctx.author.id):
            raise utils.NotRegistered(ctx.author)
        elif ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'options', 'stats', 'description', 'set', and 'remove'")
            return

    @user.command(name="options", description="List your current user options")
    async def _options(self, ctx):
        """Currently available user options:
        rich_embeds: whether Talos will embed messages for you if guild options allow it
        prefix: what prefix Talos will use in PMs with you"""
        out = "```"
        name_types = self.database.get_columns("user_options")
        options = self.database.get_user_options(ctx.author.id)
        for index in range(len(options)):
            if options[index] == ctx.author.id or options[index] == -1:
                continue
            option = options[index] if name_types[index][1] == "varchar" else bool(options[index])
            out += "{}: {}\n".format(name_types[index][0], option)
        out += "```"
        if out == "``````":
            await ctx.send("No options available.")
            return
        await ctx.send(out)

    @user.command(name="stats", description="List your current user stats")
    async def _stats(self, ctx):
        """Will show just about everything Talos knows about you."""
        profile = self.database.get_user(ctx.author.id)
        stats = self.database.get_command_data(ctx.author.id)
        out = "```"
        out += "Desc: {}\n".format(profile[1])
        out += "Total Invoked: {}\n".format(profile[2])
        out += "Command Stats:\n"
        for command in stats:
            out += "    {}: {}\n".format(command[0], command[1])
        out += "```"
        await ctx.send(out)

    @user.command(name="description", description="Set your user description")
    async def _description(self, ctx, *text):
        """Change what the user description on your profile is. Max size of 2048 characters."""
        self.database.set_description(ctx.author.id, ' '.join(text))
        await ctx.send("Description set.")

    @user.command(name="set", description="Set your user options")
    async def _set(self, ctx, option: str, value: str):
        """Set user options for your account. See `^help user options` for available options."""
        try:
            option_type = self.database.get_column_type("user_options", option)
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
            self.database.set_user_option(ctx.author.id, option, value)
            await ctx.send("Option {} set to `{}` for {}".format(option, value, ctx.author.display_name))
        else:
            await ctx.send("I don't recognize that option.")

    @user.command(name="remove", description="Set a user option to default")
    async def _remove(self, ctx, option):
        """Reset a user option to default. See `^help user options` for available options."""
        try:
            data_type = self.database.get_column_type("user_options", option)
        except ValueError:
            await ctx.send("Eh eh eh, letters and numbers only.")
            return
        if data_type is not None:
            self.database.set_user_option(ctx.author.id, option, None)
            await ctx.send("Option {} set to default for {}".format(option, ctx.author.display_name))
        else:
            await ctx.send("I don't recognize that option.")

    
def setup(bot):
    bot.add_cog(UserCommands(bot))
