
import discord.ext.commands as commands
import datetime as dt


class ConverterMeta(type):
    """
        Metaclass for TalosConverter objects. Provides the getattr that returns a new instance of the
        converter if generics are used
    """

    def __getitem__(cls, item):
        """
            Convert the passed values into a tuple if they're not, and unpack into the constructor
        :param item: Passed item(s) to get
        :return: New class instance from items
        """
        if not isinstance(item, tuple):
            item = (item,)
        return cls(*item)


class _TalosConverter(type, commands.Converter, metaclass=ConverterMeta):
    """
        Metaclass that will be subclassed by TalosConverters. Creates new classes on demand to be used as arguments
        to Generics in type hinting. Allows for arguments to be passed to a converter while also allowing them to be
        used in Unions or Optionals or similar
    """

    num = 0

    def __new__(mcs, *args, **kwargs):
        """
            Create a new converter. Ensure that the namespace is correct, as these are being created manually
        :param args: Arguments to the constructor
        :param kwargs: Keyword arguments to the constructor
        :return: New instance, a new class
        """
        name = mcs.__name__ + str(mcs.num)
        mcs.num += 1
        bases = (commands.Converter,)

        namespace = {
            "__module__": "utils.converters",
            "__qualname__": name,
            "__doc__": getattr(mcs, "__doc__", None),
            "convert": mcs.convert,
            **kwargs
        }

        return super().__new__(mcs, name, bases, namespace)

    def convert(cls, ctx, argument):
        """
            Take in a context and an argument, and attempt to convert the argument in some way. Return the result,
            or None
        :param ctx: d.py context of the call
        :param argument: Argument to attempt to convert
        :return: Converted argument
        """


class DateConverter(_TalosConverter):
    """
        TalosConverter, converts a string date into a date object
    """

    def __init__(cls, datefmt="%d-%m-%Y"):
        """
            Initialize this converter. Take the datefmt if given to use in date parsing
        :param datefmt: Format to look for
        """
        super().__init__(None)
        if not isinstance(datefmt, tuple):
            datefmt = (datefmt,)
        cls.datefmt = datefmt

    async def convert(cls, ctx, argument):
        """
            Convert a string into a date, if possible. Try each datefmt passed in, and if any of them succeeds return
            the result
        :param ctx: Context to use in conversion
        :param argument: Argument to convert
        :return: Date conversion of argument
        """
        argument = argument.replace("\\", "-").replace("/", "-")
        for fmt in cls.datefmt:
            try:
                parsed = dt.datetime.strptime(argument, fmt)
            except ValueError:
                continue
            return parsed.date()
        raise commands.UserInputError("No date conversion found")


class TimeConverter(_TalosConverter):
    """
        TalosConverter, converts a string time into a time object
    """

    def __init__(cls, timefmt="%I:%M %p"):
        """
            Initialize this converter. Take the timefmt if given to use in time parsing
        :param timefmt: Format to look for
        """
        super().__init__(None)
        if not isinstance(timefmt, tuple):
            timefmt = (timefmt,)
        cls.timefmt = timefmt

    async def convert(cls, ctx, argument):
        """
            Convert a string into a time, if possible. Try each timefmt passed in, and if any of them succeeds return
            the result
        :param ctx: Context to use in conversion
        :param argument: Argument to convert
        :return: Time conversion of argument
        """
        for fmt in cls.timefmt:
            try:
                parsed = dt.datetime.strptime(argument, fmt)
            except ValueError:
                continue
            return parsed.time()
        raise commands.UserInputError("No time conversion found")
