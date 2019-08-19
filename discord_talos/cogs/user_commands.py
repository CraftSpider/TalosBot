"""
    User Commands cog for Talos
    Holds all user specific commands, those things that alter a user's permissions, roles,
    Talos' knowledge of them, so on.

    Author: CraftSpider
"""
import discord
import discord.ext.commands as commands
import typing
import logging
import asyncio
import spidertools.common as utils
import spidertools.discord as dutils
import discord_talos.talossql as sql

log = logging.getLogger("talos.user")


def unused_role(ctx, role):
    """Check if a colour role is unused, or only used by the person asking it to be removed"""
    return (not len(role.members)) or (len(role.members) == 1 and role.members[0] == ctx.author)


def talos_colour(role):
    """Check if a role is a Talos Colour"""
    return role.name.startswith("<TALOS COLOR>")


def lopez_colour(role):
    """Check if a role is a Lopez Colour"""
    return role.name.startswith("LOPEZ COLOR:")


def unnamed_colour(role):
    """Check if a role is an unnamed Talos Colour"""
    return role.name.endswith("<TALOS COLOR>")


def named_colour(role):
    """Check if a role is a named Talos Colour"""
    return role.name.startswith("<TALOS COLOR>") and not role.name.endswith("<TALOS COLOR>")


class UserCommands(dutils.TalosCog):
    """These are commands that effect specific users. May change your roles in a guild, or alter your Talos-specific"""\
        """ settings and info."""

    @commands.group(aliases=["color"], signature="colour <hex-code>", description="Set your role colour",
                    invoke_without_command=True)
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def colour(self, ctx, *, colour: typing.Union[commands.ColourConverter, str]):
        """Changes the User's colour, if Talos has role permissions. Input may be a role with a name fitting the """\
            """"pattern `<TALOS COLOR> name`, or if the guild has the `any color` option enabled, input may be a """\
            """ hexadecimal colour value prefixed by `#` or `0x`. Use the word 'clear' to remove your Talos colour."""

        for role in ctx.author.roles:
            if talos_colour(role) or lopez_colour(role):
                await ctx.author.remove_roles(role)
                if unnamed_colour(role) and unused_role(ctx, role):
                    await role.delete()

        options = self.bot.database.get_guild_options(ctx.guild.id)

        # Attempt to find role. Break for cases where role won't be created
        colour_role = discord.utils.find(lambda x: x.name == f"<TALOS COLOR> {colour}", ctx.guild.roles)
        if colour_role is None and not options.any_color:
            await ctx.send("Sorry, that colour role doesn't exist, and arbitrary colour roles aren't allowed")
            return
        elif colour_role is None:
            if isinstance(colour, discord.Colour):
                colour_role = discord.utils.find(lambda x: talos_colour(x) and x.colour == colour, ctx.guild.roles)
            else:
                await ctx.send(
                    "Unrecognized colour format. Valid formats include `#123456`, `0x123456`, and some names such as "
                    "teal or orange")
                return

        if colour_role is not None:
            await ctx.author.add_roles(colour_role)
        else:
            colour_role = await ctx.guild.create_role(name="<TALOS COLOR>", colour=colour)
            try:
                await asyncio.sleep(.1)
                try:
                    await colour_role.edit(position=(ctx.guild.me.top_role.position - 1))
                except discord.errors.HTTPException:
                    pass
            except discord.errors.InvalidArgument as e:
                log.error(e.__cause__)
                log.error(e.args)
            await ctx.author.add_roles(colour_role)

        await ctx.send(f"{ctx.message.author.display_name}'s colour changed to {colour}!")

    @colour.command(name="clear", description="Remove all your colour roles")
    async def _clear(self, ctx):
        """Removes your Talos colour role, and if it's unnamed and you're the only one using it, deletes the role."""
        for role in ctx.author.roles:
            if talos_colour(role) or lopez_colour(role):
                await ctx.author.remove_roles(role)
                if unnamed_colour(role) and unused_role(ctx, role):
                    await role.delete()
        await ctx.send("Talos colour removed")

    @colour.command(name="clean", description="Remove all unused and unnamed colour roles")
    async def _clean(self, ctx):
        """Removes all unused and unnamed Talos colour roles that weren't automatically deleted when people cleared"""\
            """ their own colour roles. Hopefully this command will at some point be removed when Talos does it 100%"""\
            """ of the time reliably."""
        for role in ctx.guild.roles:
            if unnamed_colour(role) and len(role.members) == 0:
                await role.delete()
        await ctx.send("Talos colour role list cleaned")

    @colour.command(name="list", description="List named colour roles")
    async def _list(self, ctx):
        """Posts a list of all the named colour roles, if there are any."""
        result = []
        for role in ctx.guild.roles:
            if role.name.startswith("<TALOS COLOR>") and not role.name.endswith("<TALOS COLOR>"):
                result.append(role.name[14:])
        if result:
            await ctx.send("Named Colours:\n" + "\n".join(result))
        else:
            await ctx.send("No named colour roles present")

    @commands.command(description="Display current guild perms")
    @commands.guild_only()
    async def my_perms(self, ctx):
        """Has Talos display your current effective guild permissions. This is channel independent, channel-specific"""\
            """ perms aren't taken into account."""
        out = "```Guild Permissions:\n"
        out += ', '.join(map(lambda x: x[0], filter(lambda y: y[1] is True, ctx.author.guild_permissions)))
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
        user = self.database.get_user(ctx.author.id)
        if user:
            self.database.remove_item(user)
            await ctx.send("Deregistered user")
        else:
            raise dutils.NotRegistered(ctx.author)

    @commands.command(description="Display a user profile")
    async def profile(self, ctx, user: discord.User = None):
        """Displays you or another user's profile, if it exists. Defaults to your own profile, but accepts the name """\
            """of a user to display instead."""
        if user is None:
            user = ctx.author
        tal_user = self.database.get_user(user.id)
        if not tal_user:
            raise dutils.NotRegistered(user)
        fav_command = tal_user.get_favorite_command()
        description = tal_user.profile.description if tal_user.profile.description else "User has not set a description"
        if self.bot.should_embed(ctx):
            with dutils.PaginatedEmbed() as embed:
                embed.title = tal_user.profile.title
                embed.description = description
                embed.set_author(name=user.name, icon_url=user.avatar_url)
                value = f"Total Invoked Commands: {tal_user.profile.commands_invoked}\n"
                if fav_command is not None:
                    value += f"Favorite Command: `{fav_command.command_name}`, invoked {fav_command.times_invoked} " \
                             f"times."
                else:
                    value += f"Favorite Command: Unknown"
                embed.add_field(name="Command Stats", value=value)
            for page in embed:
                await ctx.send(embed=page)
        else:
            out = "```md\n"
            out += f"{user.name}\n"
            out += f"{description}\n"
            out += "# Command Stats:\n"
            out += f"-  Total Invoked: {tal_user.profile.commands_invoked}\n"
            out += f"-  Favorite Command: {fav_command.command_name}, invoked {fav_command.times_invoked} times."
            out += "```"
            await ctx.send(out)

    @commands.group(description="For checking or setting your own profile")
    async def user(self, ctx):
        """Options will show current user options, stats will display what Talos has saved about you, description """\
            """will set your user description, set will set user options, and remove will clear user options."""
        profile = self.database.get_user(ctx.author.id)
        if not profile:
            raise dutils.NotRegistered(ctx.author)
        elif ctx.invoked_subcommand is None:
            await ctx.send("Valid options are 'options', 'stats', 'title', 'description', 'set', and 'remove'")
            return
        ctx.t_user = profile

    @user.command(name="titles", description="List available titles")
    async def _titles(self, ctx):
        """Lists current titles that you have unlocked. Use the title command if you want to set your current title """\
            """to one of these"""
        titles = ctx.t_user.titles
        if len(titles) == 0:
            await ctx.send("No available titles")
            return
        out = "```"
        for title in titles:
            out += title.title + "\n"
        out += "```"
        await ctx.send(out)

    @user.command(name="title", description="Set your current title")
    async def _title(self, ctx, *, title=""):
        """If given no arguments will clear your title, if given a title will make that your title if you own that """\
            """title."""
        if title:
            result = ctx.t_user.set_title(title)
            if result:
                self.database.save_item(ctx.t_user)
                await ctx.send(f"Title successfully set to `{title}`")
            else:
                await ctx.send("You do not have that title")
        else:
            ctx.t_user.clear_title()
            self.database.save_item(ctx.t_user)
            await ctx.send("Title successfully cleared")

    @user.command(name="options", description="List your current user options")
    async def _options(self, ctx):
        """Currently available user options:
        rich_embeds: whether Talos will embed messages for you if guild options allow it
        prefix: what prefix Talos will use in PMs with you"""
        out = "```"
        options = self.database.get_user_options(ctx.author.id)
        for item in options.__slots__[1:]:
            out += f"{item}: {getattr(options, item)}\n"
        out += "```"
        if out == "``````":
            await ctx.send("No options available.")
            return
        await ctx.send(out)

    @user.command(name="stats", description="List your current user stats")
    async def _stats(self, ctx):
        """Will show just about everything Talos knows about you."""
        ctx.t_user: sql.TalosUser
        out = "```"
        out += f"Desc: {ctx.t_user.profile.description}\n"
        out += f"Total Invoked: {ctx.t_user.profile.commands_invoked}\n"
        out += "Command Stats:\n"
        for command in ctx.t_user.invoked:
            out += f"    {command.command_name}: {command.times_invoked}\n"
        out += "```"
        await ctx.send(out)

    @user.command(name="description", description="Set your user description")
    async def _description(self, ctx, *, text):
        """Change what the user description on your profile is. Max size of 2048 characters."""
        ctx.t_user.profile.description = text
        self.database.save_item(ctx.t_user.profile)
        await ctx.send("Description set.")

    @user.command(name="set", description="Set your user options")
    async def _set(self, ctx, option, value):
        """Set user options for your account. See `^help user options` for available options."""
        try:
            user_options = self.database.get_user_options(ctx.author.id)
            cur_val = getattr(user_options, option)
            if isinstance(cur_val, (bool, int)):
                if value.upper() == "ALLOW" or value.upper() == "TRUE":
                    value = True
                elif value.upper() == "FORBID" or value.upper() == "FALSE":
                    value = False
                else:
                    await ctx.send("Sorry, that option only accepts true or false values.")
                    return
            elif isinstance(cur_val, str):
                value = utils.replace_escapes(value)
            setattr(user_options, option, value)
            self.database.save_item(user_options)
            await ctx.send(f"Option {option} set to `{value}` for {ctx.author.display_name}")
        except AttributeError:
            await ctx.send("I don't recognize that option.")

    @user.command(name="remove", description="Set a user option to default")
    async def _remove(self, ctx, option):
        """Reset a user option to default. See `^help user options` for available options."""
        try:
            user_options = self.database.get_user_options(ctx.author.id)
            setattr(user_options, option, None)
            self.database.save_item(user_options)
            await ctx.send(f"Option {option} set to default for {ctx.author.display_name}")
        except AttributeError:
            await ctx.send("I don't recognize that option.")

    
def setup(bot):
    """
        Sets up the UserCommands extension. Adds the UserCommands cog to the bot
    :param bot: Bot this extension is being setup for
    """
    bot.add_cog(UserCommands(bot))
