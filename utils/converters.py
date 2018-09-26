
import discord.ext.commands as commands


class DateConverter(commands.Converter):

    async def convert(self, ctx, argument):
        print(argument)
        raise NotImplementedError("DateConverter not yet implemented")
