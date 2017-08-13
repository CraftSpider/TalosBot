"""
    User Commands cog for Talos
    Holds all user specific commands, those things that alter a user's permissions, roles,
    Talos knowledge of them, so on.

    Author: CraftSpider
"""
import discord
from discord.ext import commands


class UserCommands:
    """These commands can be used by anyone, as long as Talos is awake.\nThe effects will apply to the person using the command."""

    __slots__ = ['bot']

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def color(self, ctx, color: str):
        """Changes the User's color, if Talos has role permissions."""
        color_role = None
        if color.startswith("#") and len(color) == 7:
            for role in ctx.author.roles:
                if role.name.startswith("<TALOS COLOR>"):
                    await ctx.author.remove_roles(role)
            for role in ctx.guild.roles:
                if role.name.startswith("<TALOS COLOR>") and str(role.color) == color.lower():
                    color_role = role
            if color_role is not None:
                await ctx.author.add_roles(ctx.author, color_role)
            else:
                color_role = await ctx.guild.create_role(name="<TALOS COLOR>",
                                                         color=discord.Colour(int(color[1:], 16)))
                print(ctx.guild.me.top_role.position)
                try:
                    await color_role.edit(position=ctx.guild.me.top_role.position - 1)
                except discord.errors.InvalidArgument:
                    pass
                await ctx.author.add_roles(color_role)
            await ctx.send("{0.name}'s color changed to {1}!".format(ctx.message.author, color))
        else:
            await ctx.send("That isn't a valid color!")
    
    
def setup(bot):
    bot.add_cog(UserCommands(bot))
