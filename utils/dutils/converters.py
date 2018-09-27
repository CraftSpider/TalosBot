
import discord.ext.commands as commands
import datetime as dt


class ConverterMeta(type):

    def __getitem__(cls, item):
        if not isinstance(item, tuple):
            item = (item,)
        return cls(*item)


class _TalosConverter(type, commands.Converter, metaclass=ConverterMeta):

    num = 0

    def __new__(mcs, *args, **kwargs):
        name = mcs.__name__ + str(mcs.num)
        mcs.num += 1
        bases = (commands.Converter,)

        namespace = {
            "__module__": "utils.converters",
            "__qualname__": name,
            "convert": mcs.convert,
            **kwargs
        }

        return super().__new__(mcs, name, bases, namespace)

    def convert(cls, ctx, argument): ...


class DateConverter(_TalosConverter):

    def __init__(cls, datefmt="%d-%m-%Y"):
        super().__init__(None)
        if not isinstance(datefmt, tuple):
            datefmt = (datefmt,)
        cls.datefmt = datefmt

    async def convert(cls, ctx, argument):
        argument = argument.replace("\\", "-").replace("/", "-")
        parsed = None
        for fmt in cls.datefmt:
            try:
                parsed = dt.datetime.strptime(argument, fmt)
            except Exception as e:
                print(e)
        return dt.date(year=parsed.year, month=parsed.month, day=parsed.day)


class TimeConverter(_TalosConverter):

    def __init__(cls, timefmt="%I:%M %p"):
        super().__init__(None)
        if not isinstance(timefmt, tuple):
            timefmt = (timefmt,)
        cls.timefmt = timefmt

    async def convert(cls, ctx, argument):
        print(argument)
        parsed = None
        for fmt in cls.timefmt:
            try:
                parsed = dt.datetime.strptime(argument, fmt)
            except Exception as e:
                print(e)
        return dt.time(hour=parsed.hour, minute=parsed.minute, second=parsed.second)
