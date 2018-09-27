
import discord.ext.commands as commands
import datetime as dt


class ConverterMeta(type):

    def __getitem__(cls, item):
        if isinstance(item, tuple):
            return cls(*item)
        elif isinstance(item, dict):
            return cls(**item)
        else:
            return cls(item)


class TalosConverter(type, metaclass=ConverterMeta):
    pass


class DateConverter(TalosConverter):

    num = 0

    def __new__(mcs, datefmt=None):
        name = mcs.__name__ + str(mcs.num)
        mcs.num += 1
        bases = ()

        async def convert(self, ctx, argument):
            argument = argument.replace("\\", "-").replace("/", "-")
            parsed = dt.datetime.strptime(argument, self.datefmt)
            return dt.date(year=parsed.year, month=parsed.month, day=parsed.day)

        namespace = {"convert": convert, "datefmt": datefmt}
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, datefmt=None):
        super().__init__(datefmt)
        if datefmt is None:
            datefmt = "%d-%m-%Y"
        cls.datefmt = datefmt

    async def convert(self, ctx, argument):
        print(argument)
        argument = argument.replace("\\", "-").replace("/", "-")
        parsed = dt.datetime.strptime(argument, self.datefmt)
        return dt.date(year=parsed.year, month=parsed.month, day=parsed.day)


class TimeConverter(TalosConverter):

    def __init__(self, timefmt=None):
        if timefmt is None:
            timefmt = "%I:%M %p"
        self.timefmt = timefmt

    async def convert(self, ctx, argument):
        print(argument)
        parsed = dt.datetime.strptime(argument, self.timefmt)
        return dt.time(hour=parsed.hour, minute=parsed.minute, second=parsed.second)
