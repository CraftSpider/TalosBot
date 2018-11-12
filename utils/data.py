
import abc
import datetime as dt


class _EmptyVal:

    def __eq__(self, other):
        return isinstance(other, _EmptyVal)


_Empty = _EmptyVal()


class Row(metaclass=abc.ABCMeta):

    __slots__ = ()

    def __init__(self, row, conv_bool=False):
        if self.__class__ == Row:
            raise TypeError("Can't instantiate a non-subclassed row")

        for index in range(len(self.__slots__)):
            slot = self.__slots__[index]
            value = row[index]
            if conv_bool and (value == 0 or value == 1):
                value = bool(value)
            setattr(self, slot, value)

    def __str__(self):
        return f"{type(self).__name__}({', '.join(str(getattr(self, x)) for x in self.__slots__)})"

    def __repr__(self):
        return f"{type(self).__name__}([{', '.join(repr(getattr(self, x)) for x in self.__slots__)}])"

    def __eq__(self, other):
        for slot in self.__slots__:
            sval = getattr(self, slot, _Empty)
            oval = getattr(other, slot, _Empty)
            if sval == _Empty or oval == _Empty:
                return False
            if sval != oval:
                return False
        return True

    def to_row(self):
        out = []
        for slot in self.__slots__:
            value = getattr(self, slot)
            if isinstance(value, SqlConvertable):
                value = value.sql_safe()
            out.append(value)
        return out

    @classmethod
    def table_name(cls):
        if hasattr(cls, "TABLE_NAME"):
            return cls.TABLE_NAME
        else:
            return None


class MultiRow(metaclass=abc.ABCMeta):

    __slots__ = ("_removed",)

    def __init__(self, data):
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
        return iter(getattr(self, x) for x in self.__slots__)

    @abc.abstractmethod
    def removed_items(self): ...


class SqlConvertable(metaclass=abc.ABCMeta):

    __slots__ = ()

    def __eq__(self, other):
        return self.sql_safe() == other.sql_safe()

    @abc.abstractmethod
    def sql_safe(self): ...


class Table(Row):

    __slots__ = ("catalog", "schema", "name", "type", "engine", "version", "row_format", "num_rows", "avg_row_len",
                 "data_len", "max_data_len", "index_len", "data_free", "auto_increment", "create_time", "update_time",
                 "check_time", "table_collation", "checksum", "create_options", "table_commentx")


class Column(Row):

    __slots__ = ("catalog", "schema", "table_name", "name", "position", "default", "nullable", "type", "char_max_len",
                 "bytes_max_len", "numeric_precision", "numeric_scale", "datetime_precision", "char_set_name",
                 "collation_name", "column_type", "column_key", "extra", "privileges", "comment", "generation_expr",
                 "srs_id")


class TalosAdmin(Row):

    __slots__ = ("guild_id", "user_id")

    TABLE_NAME = "admins"


class InvokedCommand(Row):

    __slots__ = ("id", "command_name", "times_invoked")

    TABLE_NAME = "invoked_commands"


class UserTitle(Row):

    __slots__ = ("id", "title")

    TABLE_NAME = "user_titles"


class UserProfile(Row):

    __slots__ = ("id", "description", "commands_invoked", "title")

    TABLE_NAME = "user_profiles"


class UserOptions(Row):

    __slots__ = ("id", "rich_embeds", "prefix")

    TABLE_NAME = "user_options"

    def __init__(self, row):
        super().__init__(row, True)


class TalosUser(MultiRow):

    __slots__ = ("profile", "invoked", "titles", "options")

    @property
    def id(self):
        return self.profile.id

    @property
    def title(self):
        return self.profile.title

    def removed_items(self):
        return self._removed

    def get_favorite_command(self):
        return self.invoked[0]

    def add_title(self, title):
        if not self.check_title(title):
            self.titles.append(UserTitle([self.id, title]))

    def check_title(self, title):
        for user_title in self.titles:
            if user_title.title == title:
                return True
        return False

    def set_title(self, title):
        if self.check_title(title):
            self.profile.title = title
            return True
        return False

    def clear_title(self):
        self.profile.title = None

    def remove_title(self, title):
        removed = filter(lambda x: x.title == title, self.titles)
        for item in removed:
            self.titles.remove(item)
            self._removed.append(item)


class GuildOptions(Row):

    __slots__ = ("id", "rich_embeds", "fail_message", "pm_help", "any_color", "commands", "user_commands",
                 "joke_commands", "writing_prompts", "prompts_channel", "mod_log", "log_channel", "prefix", "timezone")

    TABLE_NAME = "guild_options"

    def __init__(self, row):
        super().__init__(row, True)


class PermissionRule(Row):

    __slots__ = ("id", "command", "perm_type", "target", "priority", "allow")

    TABLE_NAME = "perm_rules"

    def __init__(self, row):
        super().__init__(row, True)

    def __lt__(self, other):
        if isinstance(other, PermissionRule):
            return self.priority < other.priority

    def __gt__(self, other):
        if isinstance(other, PermissionRule):
            return self.priority > other.priority

    def get_allowed(self, ctx, default=None):
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

    __slots__ = ("id", "name", "text")

    TABLE_NAME = "guild_commands"


class EventPeriod(SqlConvertable):

    __slots__ = ("_seconds",)

    def __init__(self, period):
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
        return self._seconds

    @property
    def days(self):
        return self._seconds // 86400

    @property
    def hours(self):
        return (self._seconds % 86400) // 3600

    @property
    def minutes(self):
        return (self._seconds % 3600) // 60

    @minutes.setter
    def minutes(self, value):
        dif = value - self.minutes
        self._seconds += dif * 60

    @property
    def seconds(self):
        return self._seconds % 60

    @seconds.setter
    def seconds(self, value):
        dif = value - self.seconds
        self._seconds += dif

    def timedelta(self):
        return dt.timedelta(seconds=int(self))

    def sql_safe(self):
        return str(self)


class GuildEvent(Row):

    __slots__ = ("id", "name", "period", "last_active", "channel", "text")

    TABLE_NAME = "guild_events"

    def __init__(self, row):
        super().__init__(row, False)
        self.period = EventPeriod(self.period)


class Quote(Row):

    __slots__ = ("guild_id", "id", "author", "quote")

    TABLE_NAME = "quotes"
