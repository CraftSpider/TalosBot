
import abc


class Row(metaclass=abc.ABCMeta):

    __slots__ = ()

    def __init__(self, row, conv_bool=False):
        for index in range(len(self.__slots__)):
            slot = self.__slots__[index]
            value = row[index]
            if conv_bool and value == 0 or value == 1:
                value = bool(value)
            setattr(self, slot, value)

    def __str__(self):
        return f"{type(self).__name__}({', '.join(str(getattr(self, x)) for x in self.__slots__)})"

    def __repr__(self):
        return f"{type(self).__name__}([{', '.join(repr(getattr(self, x)) for x in self.__slots__)}])"

    def __eq__(self, other):
        for slot in self.__slots__:
            sval = getattr(self, slot, complex)
            oval = getattr(other, slot, complex)
            if sval == complex or oval == complex:
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

    @abc.abstractmethod
    def table_name(self): ...


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


class TalosAdmin(Row):

    __slots__ = ("guild_id", "user_id")

    def table_name(self):
        return "admins"


class InvokedCommand(Row):

    __slots__ = ("id", "command_name", "times_invoked")

    def table_name(self):
        return "invoked_commands"


class UserTitle(Row):

    __slots__ = ("id", "title")

    def table_name(self):
        return "user_titles"


class UserProfile(Row):

    __slots__ = ("id", "description", "commands_invoked", "title")

    def table_name(self):
        return "user_profiles"


class UserOptions(Row):

    __slots__ = ("id", "rich_embeds", "prefix")

    def __init__(self, row):
        super().__init__(row, True)

    def table_name(self):
        return "user_options"


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

    def __init__(self, row):
        super().__init__(row, True)

    def table_name(self):
        return "guild_options"


class PermissionRule(Row):

    __slots__ = ("id", "command", "perm_type", "target", "priority", "allow")

    def __init__(self, row):
        super().__init__(row, True)

    def __lt__(self, other):
        if isinstance(other, PermissionRule):
            return self.priority < other.priority

    def __gt__(self, other):
        if isinstance(other, PermissionRule):
            return self.priority > other.priority

    def table_name(self):
        return "perm_rules"


class GuildCommand(Row):

    __slots__ = ("id", "name", "text")

    def table_name(self):
        return "guild_commands"


class EventPeriod(SqlConvertable):

    __slots__ = ("days", "hours", "minutes")

    def __init__(self, period):
        if isinstance(period, EventPeriod):
            self.days = period.days
            self.hours = period.hours
            self.minutes = period.minutes
            return
        num = ""
        self.days = 0
        self.hours = 0
        self.minutes = 0
        for char in period:
            if char == "d" or char == "h" or char == "m":
                if char == "d":
                    self.days = int(num)
                elif char == "h":
                    self.hours = int(num)
                elif char == "m":
                    self.minutes = int(num)
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
        return out

    def __int__(self):
        return self.days * 86400 + self.hours * 3600 + self.minutes * 60

    def sql_safe(self):
        return str(self)


class GuildEvent(Row):

    __slots__ = ("id", "name", "period", "last_active", "channel", "text")

    def __init__(self, row):
        super().__init__(row, False)
        self.period = EventPeriod(self.period)

    def table_name(self):
        return "guild_events"
