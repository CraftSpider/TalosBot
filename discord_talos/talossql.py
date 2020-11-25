
from spidertools.common.data import Row, MultiRow
import spidertools.common as common
import spidertools.discord as dutils


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
        self.period = dutils.EventPeriod(self.period)


class Quote(Row):
    """
        Quote Table
    """

    __slots__ = ("guild_id", "id", "author", "quote")

    TABLE_NAME = "quotes"


class TalosDatabase(common.GenericDatabase):
    """
        A talos-specific variant of the generic database that provides methods to get Talos data objects,
        as well as add and remove uptimes.
    """

    def clean_guild(self, guild_id):
        """
            Remove all entries belonging to a specific guild from the database.
        :param guild_id: id of guild to clean.
        """
        for item in ["guild_options", "admins", "perm_rules", "guild_commands"]:
            self.execute(f"DELETE FROM {self._schema}.{item} WHERE guild_id = %s", [guild_id])

    # Guild option methods

    def get_guild_defaults(self):
        """
            Get all default guild option values
        :return: List of guild option default values
        """
        default = GuildOptions(self._schemadef["tables"]["guild_options"]["defaults"][0])
        return self.get_item(GuildOptions, default=default, guild_id=-1)

    def get_guild_options(self, guild_id):
        """
            Get all options for a guild. If option isn't set, returns the default for that option
        :param guild_id: id of the guild to get options of
        :return: list of the guild's options
        """
        result = self.get_item(GuildOptions, guild_id=guild_id)
        guild_defaults = self.get_guild_defaults()
        if result is None:
            guild_defaults.id = guild_id
            return guild_defaults
        else:
            for item in result.__slots__:
                if getattr(result, item) is None:
                    setattr(result, item, getattr(guild_defaults, item))
        return result

    def get_all_guild_options(self):
        """
            Get all options for all guilds.
        :return: List of all options of all guilds
        """
        return self.get_items(GuildOptions)

    # User option methods

    def get_user_defaults(self):
        """
            Get all default user option values
        :return: List of user option default values
        """
        default = UserOptions(self._schemadef["tables"]["user_options"]["defaults"][0])
        return self.get_item(UserOptions, default=default, user_id=-1)

    def get_user_options(self, user_id):
        """
            Get all options for a user. If option isn't set, returns the default for that option
        :param user_id: id of the user to get options of
        :return: list of the user's options
        """
        result = self.get_item(UserOptions, user_id=user_id)
        user_defaults = self.get_user_defaults()
        if result is None:
            user_defaults.id = user_id
            return user_defaults
        else:
            for item in result.__slots__:
                if getattr(result, item) is None:
                    setattr(result, item, getattr(user_defaults, item))
        return result

    def get_all_user_options(self):
        """
            Get all options for all users.
        :return: List of all options of all users
        """
        return self.get_items(UserOptions)

    # User profile methods

    def register_user(self, user_id):
        """
            Register a user with Talos. Creates values in user_profiles and user_options
        :param user_id: id of the user to register
        """
        options = UserOptions((user_id, None, None))
        self.save_item(options)
        profile = UserProfile((user_id, None, 0, None))
        self.save_item(profile)

    def get_user(self, user_id):
        """
            Return everything about a registered user
        :param user_id: id of the user to get profile of
        :return: TalosUser object containing the User Data or None
        """
        user_data = dict()
        user_data["profile"] = self.get_item(UserProfile, user_id=user_id)
        if user_data.get("profile") is None:
            return None

        user_data["invoked"] = self.get_items(InvokedCommand, order="times_invoked DESC", user_id=user_id)
        user_data["titles"] = self.get_items(UserTitle, user_id=user_id)
        user_data["options"] = self.get_user_options(user_id)

        return TalosUser(user_data)

    def user_invoked_command(self, user, command):
        """
            Called when a registered user invokes a command. Insert or increment the times that command has been invoked
            in invoked_commands table for that user.
        :param user_id: id of the user who invoked the command
        :param command: name of the command that was invoked
        """

        user.profile.commands_invoked += 1
        self.save_item(user.profile)
        inv_com = self.get_item(InvokedCommand, user_id=user.id, command_name=command)
        if inv_com is None:
            inv_com = InvokedCommand((user.id, command, 0))
        inv_com.times_invoked += 1
        self.save_item(inv_com)

    # Admin methods

    def get_all_admins(self):
        """
            Get all admins in all servers
        :return: list of all admins and guilds they are admin for.
        """
        return self.get_items(TalosAdmin)

    def get_admins(self, guild_id):
        """
            Get the list of admin for a specific guild
        :param guild_id: id of the guild to get the admin list for
        :return: list of admins for input guild
        """
        return self.get_items(TalosAdmin, guild_id=guild_id)

    # Perms methods

    def get_perm_rule(self, guild_id, command, perm_type, target):
        """
            Get permission rule for a specific context
        :param guild_id: id of the guild the rule applies to
        :param command: the name of the command the rule applies to
        :param perm_type: the type of permission rule
        :param target: the target of the permission rule
        :return: the priority and whether to allow this rule if it exists, or None
        """
        return self.get_item(PermissionRule, guild_id=guild_id, command=command, perm_type=perm_type,
                             target=target)

    def get_perm_rules(self, guild_id=-1, command=None, perm_type=None, target=None):
        """
            Get a list of permissions rules for a variably specific context
        :param guild_id: id of the guild to get permissions for. If None, get default rules if they exist
        :param command: name of the command to get rules for. Any command if none.
        :param perm_type: type of permissions to get. Any type if none.
        :param target: target of permissions to get. Any target if none.
        :return: List of rules fitting the context.
        """
        args = {}
        if command:
            args["command"] = command
        if perm_type:
            args["perm_type"] = perm_type
        if target:
            args["target"] = target
        return self.get_items(PermissionRule, guild_id=guild_id, **args)

    def get_all_perm_rules(self):
        """
            Get all permission rules in the database
        :return: List of all permission rules
        """
        return self.get_items(PermissionRule)

    # Custom guild commands

    def get_guild_command(self, guild_id, name):
        """
            Get the text for a custom guild command
        :param guild_id: id of the guild
        :param name: name of the command
        :return: text of the command or None
        """
        return self.get_item(GuildCommand, guild_id=guild_id, name=name)

    def get_guild_commands(self, guild_id):
        """
            Get a list of all commands for a guild, both names and internal text
        :param guild_id: id of the guild
        :return: List of commands
        """
        return self.get_items(GuildCommand, guild_id=guild_id)

    # Custom guild events

    def get_guild_event(self, guild_id, name):
        """
            Get the text and period for a custom guild event
        :param guild_id: id of the guild
        :param name: name of the event
        :return: custom guild event
        """
        return self.get_item(GuildEvent, guild_id=guild_id, name=name)

    def get_guild_events(self, guild_id):
        """
            Get all the events for a guild
        :param guild_id: id of the guild
        :return: list of custom guild events
        """
        return self.get_items(GuildEvent, guild_id=guild_id)

    # Quote methods

    def get_quote(self, guild_id, qid):
        """
            Get a specified quote from the quote table
        :param guild_id: Guild the quote is from
        :param qid: ID of the quote
        :return: Quote object, assuming quote exists
        """
        return self.get_item(Quote, guild_id=guild_id, id=qid)

    def get_random_quote(self, guild_id):
        """
            Get a random quote from the quote table
        :param guild_id: Guild the quote should be from
        :return: Quote object
        """
        return self.get_item(Quote, order="RAND()", guild_id=guild_id)

    # Uptime methods

    def add_uptime(self, uptime):
        """
            Add an uptime value to the list
        :param uptime: value of the uptime check to add
        """
        query = f"INSERT INTO {self._schema}.uptime VALUES (%s)"
        self.execute(query, [uptime])

    def get_uptime(self, start):
        """
            Get all uptimes greater than a specified value
        :param start: Value to start at for uptime collection
        :return: List of all uptimes
        """
        query = f"SELECT time FROM {self._schema}.uptime WHERE time >= %s"
        self.execute(query, [start])
        result = self._accessor._cursor.fetchall()
        return result

    def remove_uptime(self, end):
        """
            Remove all uptimes less than a specified value
        :param end: Value to end at for uptime removal
        """
        query = f"DELETE FROM {self._schema}.uptime WHERE time < %s"
        self.execute(query, [end])
