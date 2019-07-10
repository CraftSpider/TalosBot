
import abc
import datetime as dt


class _EmptyVal:
    """
        An entirely missing value, not just present but null
    """

    def __eq__(self, other):
        """
            Any _EmptyVal is equal to any other
        :param other: Other value to check equality of
        :return: Whether other is also an _EmptyVal
        """
        return isinstance(other, _EmptyVal)


_Empty = _EmptyVal()


class Row(metaclass=abc.ABCMeta):
    """
        Conceptually, a Row in a SQL database. Subclass to define a table, __slots__ is used to define
        the columns in order. Can be saved and loaded from a database
    """

    __slots__ = ()

    def __init__(self, row, conv_bool=False):
        """
            Initializer for a row. Handles magical __slots__ initialization
        :param row: Sequence of items pulled from a table
        :param conv_bool: Whether to convert 0's and 1's to boolean values or not
        """
        if self.__class__ == Row:
            raise TypeError("Can't instantiate a non-subclassed row")

        for index in range(len(self.__slots__)):
            slot = self.__slots__[index]
            value = row[index]
            if conv_bool and (value == 0 or value == 1):
                value = bool(value)
            setattr(self, slot, value)

    def __str__(self):
        """
            Convert a Row to a string. Takes the form of `Name(value1, value2, ...)`
        :return: String form of Row
        """
        return f"{type(self).__name__}({', '.join(str(getattr(self, x)) for x in self.__slots__)})"

    def __repr__(self):
        """
            Convert a Row to its repr. Takes the form of `Name(repr(value1), repr(value2), ...)`
        :return: Repr form of Row
        """
        return f"{type(self).__name__}([{', '.join(repr(getattr(self, x)) for x in self.__slots__)}])"

    def __eq__(self, other):
        """
            Check equality of one Row to another
        :param other: Other object to check equality of
        :return: Whether other object has same column names and same values in them
        """
        if not isinstance(other, Row):
            return False
        for slot in self.__slots__:
            sval = getattr(self, slot, _Empty)
            oval = getattr(other, slot, _Empty)
            if sval == _Empty or oval == _Empty:
                return False
            if sval != oval:
                return False
        return True

    def to_row(self):
        """
            Convert Row to a Sequence of correct length with correct data values
        :return: Sequence of SQL Storable values
        """
        out = []
        for slot in self.__slots__:
            value = getattr(self, slot)
            if isinstance(value, SqlConvertable):
                value = value.sql_safe()
            out.append(value)
        return out

    @classmethod
    def table_name(cls):
        """
            Get the name of the table this Row object is associated with
        :return: Name of a SQL table
        """
        if hasattr(cls, "TABLE_NAME"):
            return cls.TABLE_NAME
        else:
            return None


class MultiRow(metaclass=abc.ABCMeta):
    """
        An object containing multiple different rows, possibly from multiple tables.
        Can be saved and loaded from a Database like a Row
    """

    __slots__ = ("_removed",)

    def __init__(self, data):
        """
            Initialize this MultiRow with given data. Uses slot names to pull from dict into self attributes
        :param data: Dict of data to pull Rows or lists of Rows from
        """
        self._removed = []
        for slot in self.__slots__:
            value = data.get(slot)
            setattr(self, slot, value)

    def __iter__(self):
        """
            Return an iterable of all Row like objects or iterable of row like objects in the MultiRow.
            Override this if not all slots are Rows or iterables of rows
        :return: Iterable of rows or iterable containing rows
        """
        return self.items()

    def __eq__(self, other):
        """
            Check equality between this and another MultiRow. Works similarly to Row
        :param other: Other object to check against
        :return: Whether this object is equal to Other
        """
        if not isinstance(other, MultiRow):
            return False
        for slot in self.__slots__:
            sval = getattr(self, slot, _Empty)
            oval = getattr(self, slot, _Empty)
            if sval == _Empty or oval == _Empty:
                return False
            if sval != oval:
                return False
        return True

    def items(self):
        """
            Get an iterable of all Row like objects or iterable of row like objects in the MultiRow.
            Override this if not all slots are Rows or iterables of rows
        :return: Iterable of rows or iterable containing rows
        """
        return iter(getattr(self, x) for x in self.__slots__)

    @abc.abstractmethod
    def removed_items(self):
        """
            Return a list of any items removed from this row during its time in memory. Ensures they will be removed
            from the database when this object is saved.
        :return: List of Row objects
        """


class SqlConvertable(metaclass=abc.ABCMeta):
    """
        Class representing a type that is not a SQL safe type, but can be converted to one
        Generally used inside a Row
    """

    __slots__ = ()

    def __eq__(self, other):
        """
            Equality between SqlConvertable instances is based on whether their safe forms
            are qual to each other
        :param other: Other convertable to check with
        :return: Whether sql_safe forms are equal
        """
        if isinstance(other, SqlConvertable):
            return self.sql_safe() == other.sql_safe()
        return NotImplemented

    @abc.abstractmethod
    def sql_safe(self):
        """
            Convert this object to a form that can be stored in a SQL database. Can be any SQL safe type. This object,
            if fed into the constructor, should recreate the current SqlConvertable.
        :return: Object in a raw storable form
        """


class Table(Row):
    """
        Information Schema TABLES Table
    """

    __slots__ = ("catalog", "schema", "name", "type", "engine", "version", "row_format", "num_rows", "avg_row_len",
                 "data_len", "max_data_len", "index_len", "data_free", "auto_increment", "create_time", "update_time",
                 "check_time", "table_collation", "checksum", "create_options", "table_commentx")


class Column(Row):
    """
        Information Schema COLUMNS Table
    """

    __slots__ = ("catalog", "schema", "table_name", "name", "position", "default", "nullable", "type", "char_max_len",
                 "bytes_max_len", "numeric_precision", "numeric_scale", "datetime_precision", "char_set_name",
                 "collation_name", "column_type", "column_key", "extra", "privileges", "comment", "generation_expr")


class TalosAdmin(Row):
    """
        Talos Admins Table
    """

    __slots__ = ("guild_id", "user_id")

    TABLE_NAME = "admins"


class InvokedCommand(Row):
    """
        User Invoked Commands Table
    """

    __slots__ = ("id", "command_name", "times_invoked")

    TABLE_NAME = "invoked_commands"


class UserTitle(Row):
    """
        User Titles Table
    """

    __slots__ = ("id", "title")

    TABLE_NAME = "user_titles"


class UserProfile(Row):
    """
        User Profiles Table
    """

    __slots__ = ("id", "description", "commands_invoked", "title")

    TABLE_NAME = "user_profiles"


class UserOptions(Row):
    """
        User Options Table
    """

    __slots__ = ("id", "rich_embeds", "prefix")

    TABLE_NAME = "user_options"

    def __init__(self, row):
        """
            Override init to set conv_bool to True
        :param row: Row to initialize with
        """
        super().__init__(row, True)


class TalosUser(MultiRow):
    """
        Talos User object. Includes a UserProfile, their titles, their invoked commands, and their options.
        Provides methods for manipulating these things
    """

    __slots__ = ("profile", "invoked", "titles", "options")

    @property
    def id(self):
        """
            Get ID of the current Talos user
        :return: user ID
        """
        return self.profile.id

    @property
    def title(self):
        """
            Get the current title of the Talos user
        :return: user title
        """
        return self.profile.title

    def removed_items(self):
        """
            Get the list of items to delete when saving this item
        :return: List of Rows to delete
        """
        return self._removed

    def get_favorite_command(self):
        """
            Get the user's most invoked command
        :return:
        """
        if len(self.invoked):
            return self.invoked[0]
        return None

    def add_title(self, title):
        """
            Add a new title that the user is allowed to use
        :param title: String title to add
        """
        if not self.check_title(title):
            self.titles.append(UserTitle([self.id, title]))

    def check_title(self, title):
        """
            Check whether a user has access to a certain title
        :param title: String title to check access of
        :return: Boolean of whether the user has the title
        """
        for user_title in self.titles:
            if user_title.title == title:
                return True
        return False

    def set_title(self, title):
        """
            Set the active title of the user, with check to ensure they have the title
        :param title: String title to set
        :return: Whether title was successfully set
        """
        if self.check_title(title):
            self.profile.title = title
            return True
        return False

    def clear_title(self):
        """
            Clear the active title of the user
        """
        self.profile.title = None

    def remove_title(self, title):
        """
            Remove a title from the user's access
        :param title: String title to remove
        """
        removed = filter(lambda x: x.title == title, self.titles)
        for item in removed:
            self.titles.remove(item)
            self._removed.append(item)


class GuildOptions(Row):
    """
        Guild Options Table
    """

    __slots__ = ("id", "rich_embeds", "fail_message", "pm_help", "any_color", "commands", "user_commands",
                 "joke_commands", "writing_prompts", "prompts_channel", "mod_log", "log_channel", "prefix", "timezone")

    TABLE_NAME = "guild_options"

    def __init__(self, row):
        """
            Override initialization to set conv_bool to True
        :param row: Row to initialize with
        """
        super().__init__(row, True)


class PermissionRule(Row):
    """
        Permission Rule Table
    """

    __slots__ = ("id", "command", "perm_type", "target", "priority", "allow")

    TABLE_NAME = "perm_rules"

    def __init__(self, row):
        """
            Override initialization to set conv_bool to True
        :param row: Row to initialize with
        """
        super().__init__(row, True)

    def __lt__(self, other):
        """
            Check if this rule's priority is less than another rule's
        :param other: Other rule to check
        :return: Whether this rule is less than
        """
        if isinstance(other, PermissionRule):
            return self.priority < other.priority
        return NotImplemented

    def __gt__(self, other):
        """
            Check if this rule's priority is greater than another rule's
        :param other: Other rule to check
        :return: Whether this rule is greater than
        """
        if isinstance(other, PermissionRule):
            return self.priority > other.priority
        return NotImplemented

    def get_allowed(self, ctx, default=None):
        """
            Check whether this permission is satisfied in the given context
        :param ctx: d.py Context to check against
        :param default: Value to return if rule is irrelevant in given context
        :return: Boolean whether rule is satisfied or default
        """
        if self.perm_type == "user":
            if self.target == str(ctx.author):
                return self.allow
        elif self.perm_type == "role":
            for role in ctx.author.roles:
                if self.target == str(role):
                    return self.allow
        elif self.perm_type == "channel":
            if self.target == str(ctx.channel):
                return self.allow
        elif self.perm_type == "guild":
            return self.allow
        else:
            raise AttributeError("self.perm_type of unknown value")
        return default


class GuildCommand(Row):
    """
        Guild Command Table
    """

    __slots__ = ("id", "name", "text")

    TABLE_NAME = "guild_commands"


class EventPeriod(SqlConvertable):
    """
        Represents the period of time used between runs in an EventLoop. Similar to a timedelta, but
        functions slightly differently
    """

    __slots__ = ("_seconds",)

    def __new__(cls, period):
        """
            Create a new EventPeriod. If input is None, then we return None instead of a new
            EventPeriod
        :param period: object to create a new EventPeriod from
        :return: Newly created EventPeriod, or None
        """
        if period is None:
            return None
        else:
            return super().__new__(cls)

    def __init__(self, period):
        """
            Initialize an EventPeriod. If input is an EventPeriod, we create a copy.
            Otherwise we read out a string into our memory.
        :param period: Either EventPeriod to copy, or a string to read
        """
        if isinstance(period, EventPeriod):
            self._seconds = period._seconds
            return
        num = ""
        self._seconds = 0
        for char in period:
            if char == "d" or char == "h" or char == "m" or char == "s":
                if char == "d":
                    self._seconds += int(num) * 86400
                elif char == "h":
                    self._seconds += int(num) * 3600
                elif char == "m":
                    self._seconds += int(num) * 60
                elif char == "s":
                    self._seconds += int(num)
                num = ""
            elif "0" <= char <= "9":
                num += char

    def __str__(self):
        """
            Convert an EventPeriod into its string representation
        :return: String form of EventPeriod
        """
        out = ""
        if self.days:
            out += f"{self.days}d"
        if self.hours:
            out += f"{self.hours}h"
        if self.minutes:
            out += f"{self.minutes}m"
        if self.seconds:
            out += f"{self.seconds}s"
        return out

    def __int__(self):
        """
            Convert to integer representation, the number of seconds in this period in total
        :return: Seconds in EventPeriod
        """
        return self._seconds

    @property
    def days(self):
        """
            Get the number of days in this period
        :return: Number of days in the period
        """
        return self._seconds // 86400

    @property
    def hours(self):
        """
            Get the number of whole hours in this period, minus days
        :return: Number of hours in the period
        """
        return (self._seconds % 86400) // 3600

    @property
    def minutes(self):
        """
            Get the number of whole minutes in this period, minus hours and days
        :return: Number of minutes in this period
        """
        return (self._seconds % 3600) // 60

    @minutes.setter
    def minutes(self, value):
        """
            Set the number of minutes in this period. Should be a number between 0-59
        :param value: Number of minutes to set to
        """
        dif = value - self.minutes
        self._seconds += dif * 60

    @property
    def seconds(self):
        """
            Get the number of whole seconds in this period, minus greater values
        :return: Number of seconds in this period
        """
        return self._seconds % 60

    @seconds.setter
    def seconds(self, value):
        """
            Set the number of seconds in this period. Should be a number between 0-59
        :param value:
        :return:
        """
        dif = value - self.seconds
        self._seconds += dif

    def timedelta(self):
        """
            Get the timedelta representation of this period
        :return: timedelta object matching this period
        """
        return dt.timedelta(seconds=int(self))

    def sql_safe(self):
        """
            Convert this period to a string to store in a SQL database
        :return: String for storage in database
        """
        return str(self)


class GuildEvent(Row):
    """
        Guild Event Table
    """

    __slots__ = ("id", "name", "period", "last_active", "channel", "text")

    TABLE_NAME = "guild_events"

    def __init__(self, row):
        """
            Override initialization to convert string period to an EventPeriod
        :param row: Row to use in initialization
        """
        super().__init__(row)
        self.period = EventPeriod(self.period)


class Quote(Row):
    """
        Quote Table
    """

    __slots__ = ("guild_id", "id", "author", "quote")

    TABLE_NAME = "quotes"
