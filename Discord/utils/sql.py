
import utils.data as data

import logging
import re
import mysql.connector.abstracts as mysql_abstracts

log = logging.getLogger("talos.utils")

# Default priority levels
_levels = {
    "guild": 10,
    "channel": 20,
    "role": 30,
    "user": 40
}


class EmptyCursor(mysql_abstracts.MySQLCursorAbstract):

    __slots__ = ()

    DEFAULT_ONE = None
    DEFAULT_ALL = list()

    def __init__(self):
        """Init stub"""
        super().__init__()

    def __iter__(self):
        """Iterator stub"""
        return iter(self.fetchone, self.DEFAULT_ONE)

    def callproc(self, procname, args=()):
        """Callproc stub"""
        pass

    def close(self):
        """Close stub"""
        pass

    def execute(self, query, params=None, multi=False):
        """Execute stub"""
        pass

    def executemany(self, operation, seqparams):
        """Executemany stub"""
        pass

    def fetchone(self):
        """Fetchone stub"""
        return self.DEFAULT_ONE

    def fetchmany(self, size=1):
        """Fetchmany stub"""
        return self.DEFAULT_ALL

    def fetchall(self):
        """Fetchall stub"""
        return self.DEFAULT_ALL

    @property
    def description(self):
        """Description stub"""
        return tuple()

    @property
    def rowcount(self):
        """Rowcount stub"""
        return 0

    @property
    def lastrowid(self):
        """Lastrowid stub"""
        return None


talos_create_schema = "CREATE SCHEMA talos_data DEFAULT CHARACTER SET utf8"
talos_create_table = "CREATE TABLE `{}` ({}) ENGINE=InnoDB DEFAULT CHARSET=utf8"
talos_add_column = "ALTER TABLE {} ADD COLUMN {} {}".format("{}", "{}", "{}")  # Makes pycharm not complain
talos_remove_column = "ALTER TABLE {} DROP COLUMN {}".format("{}", "{}")
talos_modify_column = "ALTER TABLE {} MODIFY COLUMN {}".format("{}", "{}")
talos_tables = {
    "guild_options": {
        "columns": ["`guild_id` bigint(20) NOT NULL", "`rich_embeds` tinyint(1) DEFAULT NULL",
                    "`fail_message` tinyint(1) DEFAULT NULL", "`pm_help` tinyint(1) DEFAULT NULL",
                    "`any_color` tinyint(1) DEFAULT NULL", "`commands` tinyint(1) DEFAULT NULL",
                    "`user_commands` tinyint(1) DEFAULT NULL", "`joke_commands` tinyint(1) DEFAULT NULL",
                    "`writing_prompts` tinyint(1) DEFAULT NULL", "`prompts_channel` varchar(64) DEFAULT NULL",
                    "`prefix` varchar(32) DEFAULT NULL", "`timezone` varchar(5) DEFAULT NULL"],
        "primary": "PRIMARY KEY (`guild_id`)",
        "defaults": [(-1, True, False, False, True, True, True, True, False, "prompts", "^", "UTC")]
    },
    "admins": {
        "columns": ["`guild_id` bigint(20) NOT NULL", "`opname` bigint(20) NOT NULL"],
        "primary": "PRIMARY KEY (`guild_id`,`opname`)"
    },
    "perm_rules": {
        "columns": ["`guild_id` bigint(20) NOT NULL", "`command` varchar(255) NOT NULL",
                    "`perm_type` varchar(32) NOT NULL", "`target` varchar(255) NOT NULL",
                    "`priority` int(11) NOT NULL", "`allow` tinyint(1) NOT NULL"],
        "primary": "PRIMARY KEY (`guild_id`,`command`,`perm_type`,`target`)"
    },
    "uptime": {
      "columns": ["`time` bigint(20) NOT NULL"],
      "primary": "PRIMARY KEY (`time`)"
    },
    "user_options": {
        "columns": ["`user_id` bigint(20) NOT NULL", "`rich_embeds` tinyint(1) DEFAULT NULL",
                    "`prefix` varchar(32) DEFAULT NULL"],
        "primary": "PRIMARY KEY (`user_id`)",
        "defaults": [(-1, 1, "^")]
    },
    "user_profiles": {
        "columns": ["`user_id` bigint(20) NOT NULL", "`description` text",
                    "`commands_invoked` int(11) NOT NULL DEFAULT '0'", "`title` text"],
        "primary": "PRIMARY KEY (`user_id`)"
    },
    "user_titles": {
        "columns": ["`user_id` bigint(20) NOT NULL", "`title` varchar(255) NOT NULL"],
        "primary": "PRIMARY KEY (`user_id`,`title`)"
    },
    "invoked_commands": {
        "columns": ["`user_id` bigint(20) NOT NULL", "`command_name` varchar(32) NOT NULL",
                    "`times_invoked` int(11) NOT NULL DEFAULT '1'"],
        "primary": "PRIMARY KEY (`command_name`,`user_id`)"
    },
    "guild_commands": {
        "columns": ["`guild_id` bigint(20) NOT NULL", "`name` varchar(32) NOT NULL", "`text` text NOT NULL"],
        "primary": "PRIMARY KEY (`guild_id`,`name`)"
    }
}


class TalosDatabase:
    """
        Class for handling a Talos connection to a MySQL database that fits the schema expected by Talos.
        (Schema matching can be enforced with verify_schema)
    """

    __slots__ = ("_sql_conn", "_cursor", "_guild_cache")

    def __init__(self, sql_conn):
        """
            Initializes a TalosDatabase object. If passed None, then it replaces the cursor with a dummy class.
        :param sql_conn: MySQL connection object.
        """
        if sql_conn is not None:
            self._sql_conn = sql_conn
            self._cursor = sql_conn.cursor()
        else:
            self._sql_conn = None
            self._cursor = EmptyCursor()
        self._guild_cache = None

    def verify_schema(self):
        """
            Verifies the schema of the connected Database. If the expected schema doesn't exist, or it doesn't match the
            expected table forms, it will be updated to match.
        """
        if self.is_connected():
            self._cursor.execute("SELECT * FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = 'talos_data'")
            if self._cursor.fetchone():
                log.info("found schema talos_data")
            else:
                log.warning("talos_data doesn't exist, creating schema")
                self._cursor.execute(talos_create_schema)
            for table in talos_tables:
                self._cursor.execute(
                    "SELECT * FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'talos_data' AND TABLE_NAME = %s",
                    [table]
                )
                if self._cursor.fetchone():
                    log.info("Found table {}".format(table))

                    from collections import defaultdict
                    columns = defaultdict(lambda: [0, ""])
                    self._cursor.execute(
                        "SELECT COLUMN_NAME, DATA_TYPE FROM information_schema.COLUMNS WHERE TABLE_NAME = %s",
                        [table]
                    )
                    for item in self._cursor:
                        columns[item[0]][0] += 1
                        columns[item[0]][1] = item[1]
                    for item in talos_tables[table]["columns"]:
                        details = re.search(r"`(.*?)` (\w+)", item)
                        name, col_type = details.group(1), details.group(2)
                        columns[name][0] += 2
                        columns[name][1] = columns[name][1] == col_type

                    for name in columns:
                        exists, type_match = columns[name]
                        if exists == 1:
                            log.warning("  Found column {} that shouldn't exist, removing".format(name))
                            self._cursor.execute(talos_remove_column.format(table, name))
                        elif exists == 2:
                            log.warning("  Could not find column {}, creating column".format(name))
                            column_spec = next(filter(lambda x: x.find("`{}`".format(name)) > -1,
                                                      talos_tables[table]["columns"]))
                            column_index = talos_tables[table]["columns"].index(column_spec)
                            if column_index == 0:
                                column_place = "FIRST"
                            else:
                                column_place = "AFTER " +\
                                               re.search(
                                                   r"`(.*?)`",
                                                   talos_tables[table]["columns"][column_index-1]
                                               ).group(1)
                            self._cursor.execute(talos_add_column.format(table, column_spec, column_place))
                        elif exists == 3 and type_match is not True:
                            log.warning("  Column {} didn't match expected type, attempting to fix.".format(name))
                            column_spec = next(filter(lambda x: x.find("`{}`".format(name)) > -1,
                                                      talos_tables[table]["columns"]))
                            print(talos_modify_column.format(table, column_spec))
                            self._cursor.execute(talos_modify_column.format(table, column_spec))
                        else:
                            log.info("  Found column {}".format(name))
                else:
                    log.info("Could not find table {}, creating table".format(table))
                    self._cursor.execute(
                        talos_create_table.format(
                            table, ',\n'.join(talos_tables[table]["columns"] + [talos_tables[table]["primary"]])
                        )
                    )
            for table in talos_tables:
                if talos_tables[table].get("defaults") is not None:
                    for values in talos_tables[table]["defaults"]:
                        self._cursor.execute("REPLACE INTO {} VALUES {}".format(table, values))

    def clean_guild(self, guild_id):
        """
            Remove all entries belonging to a specific guild from the database.
        :param guild_id: id of guild to clean.
        """
        for item in ["guild_options", "admins", "perm_rules", "guild_commands"]:
            self._cursor.execute("DELETE FROM {} WHERE guild_id = %s".format(item), [guild_id])

    def commit(self):
        """
            Commits any changes to the SQL database.
        :return: Whether a commit successfully occurred
        """
        log.debug("Committing data")
        if self._sql_conn:
            self._sql_conn.commit()
            return True
        return False

    def is_connected(self):
        """
            Checks whether we are currently connected to a database
        :return: Whether the connection exists and the cursor isn't an EmptyCursor.
        """
        return self._sql_conn is not None and not isinstance(self._cursor, EmptyCursor)

    def new_connection(self, sql_conn):
        self.commit()
        if self._sql_conn:
            self._sql_conn.close()
        if sql_conn is not None:
            self._sql_conn = sql_conn
            self._cursor = sql_conn.cursor()
        else:
            self._sql_conn = None
            self._cursor = EmptyCursor()

    def raw_exec(self, statement):
        """
            Executes a SQL statement raw and returns the result. Should only be used in dev operations.
        :param statement: SQL statement to execute.
        :return: The result of a cursor fetchall after the statement executes.
        """
        self._cursor.execute(statement)
        return self._cursor.fetchall()

    # Meta methods

    def get_column_type(self, table_name, column_name):
        """
            Gets the type of a specific column
        :param table_name: Name of the table containing the column
        :param column_name: Name of the column to check
        :return: The type of the given column, or None
        """
        query = "SELECT DATA_TYPE FROM information_schema.COLUMNS WHERE TABLE_NAME = %s AND COLUMN_NAME = %s"
        self._cursor.execute(query, [table_name, column_name])
        result = self._cursor.fetchone()
        if result is not None and isinstance(result, (list, tuple)):
            result = result[0]
        return result

    def get_columns(self, table_name):
        """
            Gets the column names and types of a specified table
        :param table_name: Name of the table to retrieve columnns from
        :return: List of column names and data types, or None if table doesn't exist
        """
        query = "SELECT COLUMN_NAME, DATA_TYPE FROM information_schema.COLUMNS WHERE TABLE_NAME = %s"
        self._cursor.execute(query, [table_name])
        result = self._cursor.fetchall()
        if len(result) is 0:
            return None
        return result

    # Guild option methods

    def get_guild_defaults(self):
        """
            Get all default guild option values
        :return: List of guild option default values
        """
        query = "SELECT * FROM guild_options WHERE guild_id = -1"
        self._cursor.execute(query)
        result = self._cursor.fetchone()
        if result:
            return data.GuildOptions(self, result)
        else:
            return data.GuildOptions(self, talos_tables["guild_options"]["defaults"][0])

    def get_guild_options(self, guild_id):
        """
            Get all options for a guild. If option isn't set, returns the default for that option
        :param guild_id: id of the guild to get options of
        :return: list of the guild's options
        """
        query = "SELECT * FROM guild_options WHERE guild_id = %s"
        self._cursor.execute(query, [guild_id])
        result = self._cursor.fetchone()
        guild_defaults = self.get_guild_defaults()
        guild_data = []
        if result is None:
            return guild_defaults
        else:
            rows = self.get_columns("guild_options")
            for item in range(len(result)):
                if result[item] is None:
                    guild_data.append(getattr(guild_defaults, rows[item][0]))
                else:
                    guild_data.append(result[item])
        return data.GuildOptions(self, guild_data)

    def get_all_guild_options(self):
        """
            Get all options for all guilds.
        :return: List of all options of all guilds
        """
        query = "SELECT * FROM guild_options"
        self._cursor.execute(query)
        out = []
        for row in self._cursor:
            out.append(data.GuildOptions(self, row))
        return out

    def set_guild_option(self, guild_id, option_name, value):
        """
            Set an option for a specific guild
        :param guild_id: id of the guild to set option
        :param option_name: option to set in the guild
        :param value: thing to set option to
        """
        if re.match("[^a-zA-Z0-9_-]", option_name):
            raise ValueError("SQL Injection Detected!")
        query = "INSERT INTO guild_options (guild_id, {0}) VALUES (%s, %s) "\
                "ON DUPLICATE KEY UPDATE "\
                "{0} = VALUES({0})".format(option_name)
        self._cursor.execute(query, [guild_id, value])

    def remove_guild_option(self, guild_id, option_name):
        """
            Clear a guild option, resetting it to null
        :param guild_id: id to clear option of
        :param option_name: option to clear
        """
        if re.match("[^a-zA-Z0-9_-]", option_name):
            raise ValueError("SQL Injection Detected!")
        query = "UPDATE guild_options SET {} = null WHERE guild_id = %s".format(option_name)
        self._cursor.execute(query, [guild_id])

    # User option methods

    def get_user_defaults(self):
        """
            Get all default user option values
        :return: List of user option default values
        """
        query = "SELECT * FROM user_options WHERE user_id = -1"
        self._cursor.execute(query)
        result = self._cursor.fetchone()
        if result:
            return data.UserOptions(self, result)
        else:
            return data.UserOptions(self, talos_tables["user_options"]["defaults"][0])

    def get_user_options(self, user_id):
        """
            Get all options for a user. If option isn't set, returns the default for that option
        :param user_id: id of the user to get options of
        :return: list of the user's options
        """
        query = "SELECT * FROM user_options WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        result = self._cursor.fetchone()
        user_defaults = self.get_user_defaults()
        user_data = []
        if result is None:
            return user_defaults
        else:
            rows = self.get_columns("user_options")
            for item in range(len(result)):
                if result[item] is None:
                    user_data.append(getattr(user_defaults, rows[item][0]))
                else:
                    user_data.append(result[item])

        return data.UserOptions(self, user_data)

    def get_all_user_options(self):
        """
            Get all options for all users.
        :return: List of all options of all users
        """
        query = "SELECT * FROM user_options"
        self._cursor.execute(query)
        out = []
        for row in self._cursor:
            out.append(data.UserOptions(self, row))
        return out

    def set_user_option(self, user_id, option_name, value):
        """
            Set an option for a specific user
        :param user_id: id of the user to set option
        :param option_name: option to set of the user
        :param value: thing to set option to
        """
        if re.match("[^a-zA-Z0-9_-]", option_name):
            raise ValueError("SQL Injection Detected!")
        query = "INSERT INTO user_options (user_id, {0}) VALUES (%s, %s) "\
                "ON DUPLICATE KEY UPDATE "\
                "{0} = VALUES({0})".format(option_name)
        self._cursor.execute(query, [user_id, value])

    def remove_user_option(self, user_id, option_name):
        """
            Clear a user option, resetting it to null
        :param user_id: id to clear option of
        :param option_name: option to clear
        """
        if re.match("[^a-zA-Z0-9_-]", option_name):
            raise ValueError("SQL Injection Detected!")
        query = "UPDATE user_options SET {} = null WHERE user_id = %s".format(option_name)
        self._cursor.execute(query, [user_id])

    # User profile methods

    def register_user(self, user_id):
        """
            Register a user with Talos. Creates values in user_profiles and user_options
        :param user_id: id of the user to register
        """
        query = "INSERT INTO user_options (user_id) VALUES (%s)"
        self._cursor.execute(query, [user_id])
        query = "INSERT INTO user_profiles (user_id) VALUES (%s)"
        self._cursor.execute(query, [user_id])

    def deregister_user(self, user_id):
        """
            De-register a user from Talos. Removes values in user_profiles, user_options, and invoked_commands.
        :param user_id: id of user to remove
        """
        query = "DELETE FROM user_options WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        query = "DELETE FROM user_profiles WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        query = "DELETE FROM invoked_commands WHERE user_id = %s"
        self._cursor.execute(query, [user_id])

    def get_user(self, user_id):
        """
            Return everything about a registered user
        :param user_id: id of the user to get profile of
        :return: TalosUser object containing the User Data or None
        """
        user_data = {}
        query = "SELECT * FROM user_profiles WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        user_data["profile"] = self._cursor.fetchone()
        if user_data.get("profile") is None:
            return None

        query = "SELECT command_name, times_invoked FROM invoked_commands WHERE user_id = %s ORDER BY times_invoked"
        self._cursor.execute(query, [user_id])
        user_data["invoked"] = self._cursor.fetchall()

        query = "SELECT title FROM user_titles WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        user_data["titles"] = self._cursor.fetchall()

        user_data["options"] = self.get_user_options(user_id)

        return data.TalosUser(self, user_data)

    def set_description(self, user_id, desc):
        """
            Set the description of a user
        :param user_id: id of the user to set the description of
        :param desc: thing to set description to
        """
        query = "UPDATE user_profiles SET description = %s WHERE user_id = %s"
        self._cursor.execute(query, [desc, user_id])

    def add_title(self, user_id, title):
        """
            Add a title to a user
        :param user_id: id of the user to add the title to
        :param title: title to give the user access to
        """
        query = "INSERT INTO user_titles VALUES (%s, %s)"
        self._cursor.execute(query, [user_id, title])

    def remove_title(self, user_id, title):
        """
            Remove a title from a user
        :param user_id: id of the user to remove the title from
        :param title: title to remove from the user
        """
        query = "DELETE FROM user_titles WHERE user_id = %s AND title = %s"
        self._cursor.execute(query, [user_id, title])

    def set_title(self, user_id, title):
        """
            Set the title of a user
        :param user_id: id of the user to set the title for
        :param title: the title to set for the user
        """
        if title is None:
            query = "UPDATE user_profiles SET title = NULL WHERE user_id = %s"
            self._cursor.execute(query, [user_id])
        else:
            query = "UPDATE user_profiles SET title = %s WHERE user_id = %s"
            self._cursor.execute(query, [title, user_id])

    def user_invoked_command(self, user_id, command):
        """
            Called when a registered user invokes a command. Insert or increment the times that command has been invoked
            in invoked_commands table for that user.
        :param user_id: id of the user who invoked the command
        :param command: name of the command that was invoked
        """
        query = "UPDATE user_profiles SET commands_invoked = commands_invoked + 1 WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        query = "INSERT INTO invoked_commands (user_id, command_name) VALUES (%s, %s) " \
                "ON DUPLICATE KEY UPDATE " \
                "times_invoked = times_invoked + 1"
        self._cursor.execute(query, [user_id, command])

    # Admin methods

    def get_all_admins(self):
        """
            Get all admins in all servers
        :return: list of all admins and guilds they are admin for.
        """
        query = "SELECT guild_id, opname FROM admins"
        self._cursor.execute(query)
        out = []
        for row in self._cursor:
            out.append(row)
        return out

    def get_admins(self, guild_id):
        """
            Get the list of admin for a specific guild
        :param guild_id: id of the guild to get the admin list for
        :return: list of admins for input guild
        """
        query = "SELECT opname FROM admins WHERE guild_id = %s"
        self._cursor.execute(query, [guild_id])
        out = []
        for row in self._cursor:
            out.append(row[0])
        return out

    def add_admin(self, guild_id, admin_name):
        """
            Add an admin to a guild
        :param guild_id: id of the guild to add admin to
        :param admin_name: id of the admin to add to the guild
        """
        query = "INSERT INTO admins VALUES (%s, %s)"
        self._cursor.execute(query, [guild_id, admin_name])

    def remove_admin(self, guild_id, admin_name):
        """
            Remove an admin from a guild
        :param guild_id: id of the guild to remove admin from
        :param admin_name: id of the admin to be removed from the guild
        """
        query = "DELETE FROM admins WHERE guild_id = %s AND opname = %s"
        self._cursor.execute(query, [guild_id, admin_name])

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
        query = "SELECT * FROM perm_rules WHERE guild_id = %s AND command = %s AND perm_type = %s AND"\
                " target = %s"
        self._cursor.execute(query, [guild_id, command, perm_type, target])
        response = self._cursor.fetchone()
        return data.PermissionRule(self, response)

    def get_perm_rules(self, guild_id=-1, command=None, perm_type=None, target=None):
        """
            Get a list of permissions rules for a variably specific context
        :param guild_id: id of the guild to get permissions for. If None, get default rules if they exist
        :param command: name of the command to get rules for. Any command if none.
        :param perm_type: type of permissions to get. Any type if none.
        :param target: target of permissions to get. Any target if none.
        :return: List of rules fitting the context.
        """
        query = "SELECT * FROM perm_rules WHERE guild_id = %s"
        args = []
        if command or perm_type or target:
            query += " AND "
        if command:
            query += "command = %s"
            args.append(command)
            if perm_type or target:
                query += " AND "
        if perm_type:
            query += "perm_type = %s"
            args.append(perm_type)
            if target:
                query += " AND "
        if target:
            query += "target = %s"
            args.append(target)
        self._cursor.execute(query, [guild_id] + args)
        response = self._cursor.fetchall()
        out = []
        for item in response:
            out.append(data.PermissionRule(self, item))
        return out

    def get_all_perm_rules(self):
        """
            Get all permission rules in the database
        :return: List of all permission rules
        """
        query = "SELECT guild_id, command, perm_type, target, priority, allow FROM perm_rules"
        self._cursor.execute(query)
        return self._cursor.fetchall()

    def set_perm_rule(self, guild_id, command, perm_type, allow, priority=None, target=None):
        """
            Create or update a permission rule
        :param guild_id: id of the guild to set rule for
        :param command: name of the command to set rule for
        :param perm_type: type of the rule to set
        :param allow: whether to allow or forbid
        :param priority: priority of the rule
        :param target: target of the rule
        """
        if priority is None:
            priority = _levels[perm_type]
        if target is None:
            target = "SELF"
        query = "INSERT INTO perm_rules VALUES (%s, %s, %s, %s, %s, %s)"\
                "ON DUPLICATE KEY UPDATE "\
                "guild_id = VALUES(guild_id),"\
                "command = VALUES(command),"\
                "perm_type = VALUES(perm_type),"\
                "target = VALUES(target),"\
                "priority = VALUES(priority),"\
                "allow = VALUES(allow)"
        self._cursor.execute(query, [guild_id, command, perm_type, target, priority, allow])

    def remove_perm_rules(self, guild_id: int, command=None, perm_type=None, target=None):
        """
            Remove permissions rules fitting a specified context
        :param guild_id: id of the guild to remove rules from
        :param command: name of the command to remove rules for. Any if None
        :param perm_type: type of the rules to remove. Any if None
        :param target: target to remove rules for. Any if None
        """
        query = "DELETE FROM perm_rules WHERE guild_id = %s"
        if command or perm_type or target:
            query += " AND "
        args = []
        if command:
            query += "command = %s"
            args.append(command)
            if perm_type or target:
                query += " AND "
        if perm_type:
            query += "perm_type = %s"
            args.append(perm_type)
            if target:
                query += " AND "
        if target:
            query += "target = %s"
            args.append(target)
        self._cursor.execute(query, [guild_id] + args)

    # Custom guild commands

    def set_guild_command(self, guild_id, name, text):
        """
            Set the text for a custom guild command
        :param guild_id: id of the guild
        :param name: name of the command
        :param text: text of the command
        """
        query = "INSERT INTO guild_commands VALUES (%s, %s, %s) " \
                "ON DUPLICATE KEY UPDATE " \
                "guild_id = VALUES(guild_id)," \
                "name = VALUES(name)," \
                "text = VALUES(text)"
        self._cursor.execute(query, [guild_id, name, text])

    def get_guild_command(self, guild_id, name):
        """
            Get the text for a custom guild command
        :param guild_id: id of the guild
        :param name: name of the command
        :return: text of the command or None
        """
        query = "SELECT text FROM guild_commands WHERE guild_id = %s and name = %s"
        self._cursor.execute(query, [guild_id, name])
        result = self._cursor.fetchone()
        if result:
            result = result[0]
        return result

    def get_guild_commands(self, guild_id):
        """
            Get a list of all commands for a guild, both names and internal text
        :param guild_id: id of the guild
        :return: List of commands
        """
        query = "SELECT name, text FROM guild_commands WHERE guild_id = %s"
        self._cursor.execute(query, [guild_id])
        return self._cursor.fetchall()

    def remove_guild_command(self, guild_id, name):
        """
            Remove a custom guild command
        :param guild_id: id of the guild
        :param name: name of the command to remove
        """
        query = "DELETE FROM guild_commands WHERE guild_id = %s and name = %s"
        self._cursor.execute(query, [guild_id, name])

    # Uptime methods

    def add_uptime(self, uptime):
        """
            Add an uptime value to the list
        :param uptime: value of the uptime check to add
        """
        query = "INSERT INTO uptime VALUES (%s)"
        self._cursor.execute(query, [uptime])

    def get_uptime(self, start):
        """
            Get all uptimes greater than a specified value
        :param start: Value to start at for uptime collection
        :return: List of all uptimes
        """
        query = "SELECT time FROM uptime WHERE time >= %s"
        self._cursor.execute(query, [start])
        result = self._cursor.fetchall()
        return result

    def remove_uptime(self, end):
        """
            Remove all uptimes less than a specified value
        :param end: Value to end at for uptime removal
        """
        query = "DELETE FROM uptime WHERE time < %s"
        self._cursor.execute(query, [end])
