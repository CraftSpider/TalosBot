import discord
from discord.ext import commands


class UserCommands:
    """These commands can be used by anyone, as long as Talos is awake.\nThe effects will apply to the person using the command."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def color(self, ctx, color: str):
        color_role = None
        if color.startswith("#") and len(color) == 7:
            for role in ctx.message.author.roles:
                if role.name.startswith("<TALOS COLOR>"):
                    await self.bot.remove_roles(ctx.message.author, role)
            for role in ctx.message.server.roles:
                if role.name.startswith("<TALOS COLOR>") and str(role.color) == color.lower():
                    color_role = role
            if color_role is not None:
                await self.bot.add_roles(ctx.message.author, color_role)
            else:
                color_role = await self.bot.create_role(ctx.message.server, name="<TALOS COLOR>",
                                                        color=discord.Colour(int(color[1:], 16)))
                await self.bot.move_role(ctx.message.server, color_role, ctx.message.server.me.top_role.position - 1)
                await self.bot.add_roles(ctx.message.author, color_role)
            await self.bot.say("{0.name}'s color changed to {1}!".format(ctx.message.author, color))
        else:
            await self.bot.say("That isn't a valid color!")
    
    
def setup(bot):
    bot.add_cog(UserCommands(bot))
