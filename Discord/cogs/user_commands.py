"""
    User Commands cog for Talos
    Holds all user specific commands, those things that alter a user's permissions, roles,
    Talos' knowledge of them, so on.

    Author: CraftSpider
"""
import discord
import discord.ext.commands as commands
import discord.errors as errors
import logging
import asyncio
import utils
import re

log = logging.getLogger("talos.user")


def space_replace(match):
    print(match.group(1))
    if match.group(1):
        return "\\"*int(len(match.group(0)) / 2) + " "
    else:
        return " "


class UserCommands(utils.TalosCog):
    """These commands can be used by anyone, as long as Talos is awake.\n"""\
        """The effects will apply to the person using the command."""

    @commands.command(aliases=["color"], signature="colour <hex-code>", description="Set your role colour")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def colour(self, ctx, colour):
        """Changes the User's colour, if Talos has role permissions."""\
            """ Input must be a hexadecimal colour prefixed by `#` or the word 'clear' to remove all Talos colours."""
        # If we want to remove Talos Colour
        if colour == "clear":
            for role in ctx.author.roles:
                if role.name.startswith("<TALOS COLOR>") or role.name.startswith("LOPEZ COLOR:"):
                    await ctx.author.remove_roles(role)
                    if not len(role.members):
                        await role.delete()
            await ctx.send("Talos colour removed")
            return

        if not colour.startswith("#") or len(colour) is not 7 and len(colour) is not 4:
            await ctx.send("That isn't a valid hexadecimal colour!")
            return

        for role in ctx.author.roles:
            if role.name.startswith("<TALOS COLOR>") or role.name.startswith("LOPEZ COLOR:"):
                await ctx.author.remove_roles(role)
                if not len(role.members):
                    await role.delete()

        # Convert to hexadecimal number
        discord_colour = None
        try:
            if len(colour) == 7:
                discord_colour = discord.Colour(int(colour[1:], 16))
            elif len(colour) == 4:
                colour = colour[1:]
                result = ""
                for item in colour:
                    result += item*2
                discord_colour = discord.Colour(int(result, 16))
                colour = f"#{result}"
        except ValueError:
            await ctx.send("That isn't a valid hexadecimal colour!")
            return

        # Find and add or create and add the role.
        colour_role = discord.utils.find(lambda x: x.name.startswith("<TALOS COLOR>") and x.colour == discord_colour,
                                         ctx.guild.roles)
        if colour_role is not None:
            await ctx.author.add_roles(colour_role)
        else:
            colour_role = await ctx.guild.create_role(name="<TALOS COLOR>", colour=discord_colour)
            try:
                await asyncio.sleep(.1)
                try:
                    await colour_role.edit(position=(ctx.guild.me.top_role.position - 1))
                except errors.HTTPException:
                    pass
            except discord.errors.InvalidArgument as e:
                log.error(e.__cause__)
                log.error(e.args)
            await ctx.author.add_roles(colour_role)

        await ctx.send(f"{ctx.message.author.display_name}'s colour changed to {colour}!")

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
            raise utils.NotRegistered(ctx.author)

    @commands.command(description="Display a user profile")
    async def profile(self, ctx, user: discord.User=None):
        """Displays you or another user's profile, if it exists. Defaults to your own profile, but accepts the name """\
            """of a user to display instead."""
        if user is None:
            user = ctx.author
        tal_user = self.database.get_user(user.id)
        if not tal_user:
            raise utils.NotRegistered(user)
        favorite_command = tal_user.get_favorite_command()
        description = tal_user.profile.description if tal_user.profile.description else "User has not set a description"
        if self.bot.should_embed(ctx):
            with utils.PaginatedEmbed() as embed:
                embed.title = tal_user.profile.title
                embed.description = description
                embed.set_author(name=user.name, icon_url=user.avatar_url)
                value = f"Total Invoked Commands: {tal_user.profile.commands_invoked}\n" \
                        f"Favorite Command: `{favorite_command[0]}`, invoked {favorite_command[1]} times."
                embed.add_field(name="Command Stats", value=value)
            for page in embed:
                await ctx.send(embed=page)
        else:
            out = "```md\n"
            out += f"{user.name}\n"
            out += f"{description}\n"
            out += "# Command Stats:\n"
            out += f"-  Total Invoked: {tal_user.profile.commands_invoked}\n"
            out += f"-  Favorite Command: {favorite_command[0]}, invoked {favorite_command[1]} times."
            out += "```"
            await ctx.send(out)

    @commands.group(description="For checking or setting your own profile")
    async def user(self, ctx):
        """Options will show current user options, stats will display what Talos has saved about you, description """\
            """will set your user description, set will set user options, and remove will clear user options."""
        profile = self.database.get_user(ctx.author.id)
        if not profile:
            raise utils.NotRegistered(ctx.author)
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
            self.database.save_item(ctx.t_user)
            if result:
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
        out = "```"
        out += f"Desc: {ctx.t_user.profile.description}\n"
        out += f"Total Invoked: {ctx.t_user.profile.total_commands}\n"
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
                value = re.sub(r"(?<!\\)\\((?:\\\\)*)s", space_replace, value)
                value = re.sub(r"\\\\", r"\\", value)
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
    bot.add_cog(UserCommands(bot))
