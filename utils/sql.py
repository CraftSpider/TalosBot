
import utils.data as data

import logging
import re
import mysql.connector
import mysql.connector.abstracts as mysql_abstracts

log = logging.getLogger("talos.utils.sql")

# Default priority levels
levels = {
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


talos_create_schema = "CREATE SCHEMA {} DEFAULT CHARACTER SET utf8"
talos_create_table = "CREATE TABLE `{}` ({}) ENGINE=InnoDB DEFAULT CHARSET=utf8"
talos_add_column = "ALTER TABLE {} ADD COLUMN {} {}"
talos_remove_column = "ALTER TABLE {} DROP COLUMN {}"
talos_modify_column = "ALTER TABLE {} MODIFY COLUMN {}"
talos_create_trigger = "CREATE TRIGGER {} {} on {} {} END;"

talos_tables = {
    "guild_options": {
        "columns": ["`guild_id` bigint(20) NOT NULL", "`rich_embeds` tinyint(1) DEFAULT NULL",
                    "`fail_message` tinyint(1) DEFAULT NULL", "`pm_help` tinyint(1) DEFAULT NULL",
                    "`any_color` tinyint(1) DEFAULT NULL", "`commands` tinyint(1) DEFAULT NULL",
                    "`user_commands` tinyint(1) DEFAULT NULL", "`joke_commands` tinyint(1) DEFAULT NULL",
                    "`writing_prompts` tinyint(1) DEFAULT NULL", "`prompts_channel` varchar(64) DEFAULT NULL",
                    "`mod_log` tinyint(1) DEFAULT NULL", "`log_channel` varchar(64) DEFAULT NULL",
                    "`prefix` varchar(32) DEFAULT NULL", "`timezone` varchar(5) DEFAULT NULL"],
        "primary": "PRIMARY KEY (`guild_id`)",
        "defaults": [(-1, True, False, False, True, True, True, True, False, "prompts", False, "mod-log", "^", "UTC")]
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
    },
    "guild_events": {
        "columns": ["`guild_id` bigint(20) NOT NULL", "`name` varchar(32) NOT NULL", "`period` varchar(32) NOT NULL",
                    "`last_active` int NOT NULL", "`channel` bigint(20) NOT NULL", "`text` text NOT NULL"],
        "primary": "PRIMARY KEY (`guild_id`,`name`)"
    },
    "quotes": {
        "columns": ["`guild_id` bigint(20) NOT NULL", "`id` bigint NOT NULL", "`author` text",
                    "`quote` text"],
        "primary": "PRIMARY KEY (`guild_id`, `id`)"
    }
}
talos_triggers = {
    "quote_increment": {
        "cause": "before insert",
        "table": "quotes",
        "text": "FOR EACH ROW BEGIN SET NEW.id = (SELECT IFNULL(MAX(id), 0) + 1 FROM quotes "
                "WHERE guild_id = NEW.guild_id);"
    }
}


class TalosDatabase:
    """
        Class for handling a Talos connection to a MySQL database that fits the schema expected by Talos.
        (Schema matching can be enforced with verify_schema)
    """

    __slots__ = ("_sql_conn", "_cursor", "_username", "_password", "_schema", "_host", "_port")

    def __init__(self, address, port, username, password, schema):
        """
            Initializes a TalosDatabase object. If passed None, then it replaces the cursor with a dummy class.
        :param address: Address of the SQL database
        :param port: Port of the SQL database
        :param username: SQL username
        :param password: SQL password
        :param schema: SQL schema
        """
        self._username = username
        self._password = password
        self._schema = schema
        self._host = address
        self._port = port
        self._sql_conn = None
        self._cursor = None
        self.reset_connection()

    def verify_schema(self):
        """
            Verifies the schema of the connected Database. If the expected schema doesn't exist, or it doesn't match the
            expected table forms, it will be updated to match. This requires basically root on the database.
        """
        if not self.is_connected():
            log.warning("Attempt to verify schema when database not connected")
            return

        # Verify schema is extant
        self._cursor.execute("SELECT * FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = %s", [self._schema])
        if self._cursor.fetchone():
            log.info(f"found schema {self._schema}")
        else:
            log.warning(f"Schema {self._schema} doesn't exist, creating schema")
            self._cursor.execute(talos_create_schema.format(self._schema))

        # Verify tables match expected
        for table in talos_tables:
            if self.has_table(table):
                log.info(f"Found table {table}")

                from collections import defaultdict
                columndat = defaultdict(lambda: [0, ""])
                columns = self.get_columns(table)
                for item in columns:
                    columndat[item[0]][0] += 1
                    columndat[item[0]][1] = item[1]
                for item in talos_tables[table]["columns"]:
                    details = re.search(r"`(.*?)` (\w+)", item)
                    name, col_type = details.group(1), details.group(2)
                    columndat[name][0] += 2
                    columndat[name][1] = columndat[name][1] == col_type

                for name in columndat:
                    exists, type_match = columndat[name]
                    if exists == 1:
                        log.warning(f"  Found column {name} that shouldn't exist, removing")
                        self._cursor.execute(talos_remove_column.format(table, name))
                    elif exists == 2:
                        log.warning(f"  Could not find column {name}, creating column")
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
                        log.warning(f"  Column {name} didn't match expected type, attempting to fix.")
                        column_spec = next(filter(lambda x: x.find("`{}`".format(name)) > -1,
                                                  talos_tables[table]["columns"]))
                        self._cursor.execute(talos_modify_column.format(table, column_spec))
                    else:
                        log.info(f"  Found column {name}")
            else:
                log.info(f"Could not find table {table}, creating table")
                self._cursor.execute(
                    talos_create_table.format(
                        table, ',\n'.join(talos_tables[table]["columns"] + [talos_tables[table]["primary"]])
                    )
                )

        # Fill tables with default values
        for table in talos_tables:
            if talos_tables[table].get("defaults") is not None:
                for values in talos_tables[table]["defaults"]:
                    self._cursor.execute(f"REPLACE INTO {table} VALUES {values}")

        # Drop existing triggers
        query = "SELECT trigger_name FROM information_schema.TRIGGERS WHERE trigger_schema = SCHEMA();"
        self._cursor.execute(query)
        triggers = map(lambda x: x[0], self._cursor.fetchall())
        for trigger in triggers:
            self._cursor.execute(f"DROP TRIGGER {trigger}")

        # Add all triggers
        for name in talos_triggers:
            cause = talos_triggers[name]["cause"]
            table = talos_triggers[name]["table"]
            text = talos_triggers[name]["text"]
            self._cursor.execute(talos_create_trigger.format(name, cause, table, text))

    def clean_guild(self, guild_id):
        """
            Remove all entries belonging to a specific guild from the database.
        :param guild_id: id of guild to clean.
        """
        for item in ["guild_options", "admins", "perm_rules", "guild_commands"]:
            self._cursor.execute(f"DELETE FROM {self._schema}.{item} WHERE guild_id = %s", [guild_id])

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

    def reset_connection(self):
        """
            Reset the database connection, commit if one currently exists and make a new database connection.
            If connection fails, it is set to None and cursor is the empty cursor
        """

        if self._sql_conn:
            self.commit()
            self._sql_conn.close()

        cnx = None
        try:
            cnx = mysql.connector.connect(user=self._username, password=self._password, host=self._host,
                                          port=self._port, autocommit=True)
            if cnx is None:
                log.warning("Talos database missing, no data will be saved this session.")
            else:
                try:
                    cnx.cursor().execute(f"USE {self._schema}")
                    log.info("Talos database connection established")
                except mysql.connector.DatabaseError:
                    log.info("Talos Schema non-extant, creating")
                    try:
                        cnx.cursor().execute(f"CREATE SCHEMA {self._schema}")
                        cnx.cursor().execute(f"USE {self._schema}")
                        log.info("Talos database connection established")
                    except mysql.connector.DatabaseError:
                        log.warning("Talos Schema could not be created, dropping connection")
                        cnx = None
        except Exception as e:
            log.warning(e)
            log.warning("Database connection dropped, no data will be saved this session.")

        if cnx is not None:
            self._sql_conn = cnx
            self._cursor = cnx.cursor()
        else:
            self._sql_conn = None
            self._cursor = EmptyCursor()

    def raw_exec(self, statement, *args):
        """
            Executes a SQL statement raw and returns the result. Should only be used in dev operations.
        :param statement: SQL statement to execute.
        :return: The result of a cursor fetchall after the statement executes.
        """
        self._cursor.execute(statement, args)
        return self._cursor.fetchall()

    # Meta methods
    
    def get_tables(self):
        query = "SELECT * FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s"
        self._cursor.execute(query, [self._schema])
        return [data.Table(x) for x in self._cursor]

    def has_table(self, table):
        self._cursor.execute(
            "SELECT * FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s",
            [self._schema, table]
        )
        return self._cursor.fetchone() is not None

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

    # Generic methods

    def get_item(self, type, *, order=None, default=None, **kwargs):
        conditions = " AND ".join(f"{x} = %s" for x in kwargs)
        query = f"SELECT * FROM {self._schema}.{type.table_name()}"
        if conditions:
            query += " WHERE " + conditions
        if order:
            query += f" ORDER BY {order}"
        query += " LIMIT 1"
        self._cursor.execute(query, kwargs.values())
        result = self._cursor.fetchone()
        if result is None:
            return default
        return type(result)

    def get_items(self, type, *, limit=0, order=None, **kwargs):
        conditions = " AND ".join(f"{x} = %s" for x in kwargs)
        query = f"SELECT * FROM {self._schema}.{type.table_name()}"
        if conditions:
            query += " WHERE " + conditions
        if order:
            query += f" ORDER BY {order}"
        if limit:
            query += f" LIMIT {limit}"
        self._cursor.execute(query, kwargs.values())
        return [type(x) for x in self._cursor]

    def save_item(self, item):
        """
            Save any TalosDatabase compatible object to the database, inserting or updating that row.
        :param item: Item to save. May be a Row, a MultiRow, or any duck type of those two.
        """
        try:
            table_name = item.table_name()
            row = item.to_row()
            columns = list(map(lambda x: re.match(r"`(.*?)`", x).group(1), talos_tables[table_name]["columns"]))
            replace_str = ", ".join("%s" for _ in range(len(columns)))
            update_str = ", ".join(f"{i} = VALUES({i})" for i in columns)
            query = f"INSERT INTO {self._schema}.{table_name} VALUES ({replace_str}) "\
                    "ON DUPLICATE KEY UPDATE "\
                    f"{update_str}"
            log.debug(query)
            self._cursor.execute(query, row)
        except AttributeError:
            for row in item:
                self.save_item(row)
            try:
                removed_items = item.removed_items()
                for removed in removed_items:
                    self.remove_item(removed)
            except AttributeError:  # So iterables not having this property is just ignored
                pass

    def remove_item(self, item, general=False):
        """
            Remove any TalosDatabase compatible object from the database.
        :param item: Item to remove. May be a Row, a MultiRow, or any duck type of those two.
        :param general: Whether to delete all similar items. If true, nulls aren't included in the delete search
        """
        try:
            table_name = item.table_name()
            row = item.to_row()
            columns = list(map(lambda x: re.match(r"`(.*?)`", x).group(1), talos_tables[table_name]["columns"]))
            if not general:
                delete_str = " AND ".join(f"{i} = %s" for i in columns)
            else:
                delete_str = " AND ".join(
                    f"{columns[i]} = %s" for i in range(len(columns)) if getattr(item, item.__slots__[i]) is not None
                )
                row = list(filter(None, row))
            query = f"DELETE FROM {self._schema}.{table_name} WHERE {delete_str}"
            log.debug(query)
            self._cursor.execute(query, row)
        except AttributeError:
            for row in item:
                self.remove_item(row, general)

    # Guild option methods

    def get_guild_defaults(self):
        """
            Get all default guild option values
        :return: List of guild option default values
        """
        default = data.GuildOptions(talos_tables["guild_options"]["defaults"][0])
        return self.get_item(data.GuildOptions, default=default, guild_id=-1)

    def get_guild_options(self, guild_id):
        """
            Get all options for a guild. If option isn't set, returns the default for that option
        :param guild_id: id of the guild to get options of
        :return: list of the guild's options
        """
        query = f"SELECT * FROM {self._schema}.guild_options WHERE guild_id = %s"
        self._cursor.execute(query, [guild_id])
        result = self._cursor.fetchone()
        guild_defaults = self.get_guild_defaults()
        guild_data = []
        if result is None:
            guild_defaults.id = guild_id
            return guild_defaults
        else:
            rows = self.get_columns("guild_options")
            for item in range(len(result)):
                if result[item] is None:
                    guild_data.append(getattr(guild_defaults, rows[item][0]))
                else:
                    guild_data.append(result[item])
        return data.GuildOptions(guild_data)

    def get_all_guild_options(self):
        """
            Get all options for all guilds.
        :return: List of all options of all guilds
        """
        return self.get_items(data.GuildOptions)

    # User option methods

    def get_user_defaults(self):
        """
            Get all default user option values
        :return: List of user option default values
        """
        default = data.UserOptions(talos_tables["user_options"]["defaults"][0])
        return self.get_item(data.UserOptions, default=default, user_id=-1)

    def get_user_options(self, user_id):
        """
            Get all options for a user. If option isn't set, returns the default for that option
        :param user_id: id of the user to get options of
        :return: list of the user's options
        """
        query = f"SELECT * FROM {self._schema}.user_options WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        result = self._cursor.fetchone()
        user_defaults = self.get_user_defaults()
        user_data = []
        if result is None:
            user_defaults.id = user_id
            return user_defaults
        else:
            rows = self.get_columns("user_options")
            for item in range(len(result)):
                if result[item] is None:
                    user_data.append(getattr(user_defaults, rows[item][0]))
                else:
                    user_data.append(result[item])

        return data.UserOptions(user_data)

    def get_all_user_options(self):
        """
            Get all options for all users.
        :return: List of all options of all users
        """
        return self.get_items(data.UserOptions)

    # User profile methods

    def register_user(self, user_id):
        """
            Register a user with Talos. Creates values in user_profiles and user_options
        :param user_id: id of the user to register
        """
        query = f"INSERT INTO {self._schema}.user_options (user_id) VALUES (%s)"
        self._cursor.execute(query, [user_id])
        query = f"INSERT INTO {self._schema}.user_profiles (user_id) VALUES (%s)"
        self._cursor.execute(query, [user_id])

    def get_user(self, user_id):
        """
            Return everything about a registered user
        :param user_id: id of the user to get profile of
        :return: TalosUser object containing the User Data or None
        """
        user_data = dict()
        user_data["profile"] = self.get_item(data.UserProfile, user_id=user_id)
        if user_data.get("profile") is None:
            return None

        user_data["invoked"] = self.get_items(data.InvokedCommand, order="times_invoked", user_id=user_id)
        user_data["titles"] = self.get_items(data.UserTitle, user_id=user_id)
        user_data["options"] = self.get_user_options(user_id)

        return data.TalosUser(user_data)

    def user_invoked_command(self, user_id, command):
        """
            Called when a registered user invokes a command. Insert or increment the times that command has been invoked
            in invoked_commands table for that user.
        :param user_id: id of the user who invoked the command
        :param command: name of the command that was invoked
        """
        query = f"UPDATE {self._schema}.user_profiles SET commands_invoked = commands_invoked + 1 WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        query = f"INSERT INTO {self._schema}.invoked_commands (user_id, command_name) VALUES (%s, %s) " \
                "ON DUPLICATE KEY UPDATE " \
                "times_invoked = times_invoked + 1"
        self._cursor.execute(query, [user_id, command])

    # Admin methods

    def get_all_admins(self):
        """
            Get all admins in all servers
        :return: list of all admins and guilds they are admin for.
        """
        return self.get_items(data.TalosAdmin)

    def get_admins(self, guild_id):
        """
            Get the list of admin for a specific guild
        :param guild_id: id of the guild to get the admin list for
        :return: list of admins for input guild
        """
        return self.get_items(data.TalosAdmin, guild_id=guild_id)

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
        return self.get_item(data.PermissionRule, guild_id=guild_id, command=command, perm_type=perm_type, target=target)

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
        return self.get_items(data.PermissionRule, guild_id=guild_id, **args)

    def get_all_perm_rules(self):
        """
            Get all permission rules in the database
        :return: List of all permission rules
        """
        return self.get_items(data.PermissionRule)

    # Custom guild commands

    def get_guild_command(self, guild_id, name):
        """
            Get the text for a custom guild command
        :param guild_id: id of the guild
        :param name: name of the command
        :return: text of the command or None
        """
        return self.get_item(data.GuildCommand, guild_id=guild_id, name=name)

    def get_guild_commands(self, guild_id):
        """
            Get a list of all commands for a guild, both names and internal text
        :param guild_id: id of the guild
        :return: List of commands
        """
        return self.get_items(data.GuildCommand, guild_id=guild_id)

    # Custom guild events

    def get_guild_event(self, guild_id, name):
        """
            Get the text and period for a custom guild event
        :param guild_id: id of the guild
        :param name: name of the event
        :return: custom guild event
        """
        return self.get_item(data.GuildEvent, guild_id=guild_id, name=name)

    def get_guild_events(self, guild_id):
        """
            Get all the events for a guild
        :param guild_id: id of the guild
        :return: list of custom guild events
        """
        return self.get_items(data.GuildEvent, guild_id=guild_id)

    # Quote methods

    def get_quote(self, guild_id, qid):
        """
            Get a specified quote from the quote table
        :param guild_id: Guild the quote is from
        :param qid: ID of the quote
        :return: Quote object, assuming quote exists
        """
        return self.get_item(data.Quote, guild_id=guild_id, id=qid)

    def get_random_quote(self, guild_id):
        """
            Get a random quote from the quote table
        :param guild_id: Guild the quote should be from
        :return: Quote object
        """
        return self.get_item(data.Quote, order="RAND()", guild_id=guild_id)

    # Uptime methods

    def add_uptime(self, uptime):
        """
            Add an uptime value to the list
        :param uptime: value of the uptime check to add
        """
        query = f"INSERT INTO {self._schema}.uptime VALUES (%s)"
        self._cursor.execute(query, [uptime])

    def get_uptime(self, start):
        """
            Get all uptimes greater than a specified value
        :param start: Value to start at for uptime collection
        :return: List of all uptimes
        """
        query = f"SELECT time FROM {self._schema}.uptime WHERE time >= %s"
        self._cursor.execute(query, [start])
        result = self._cursor.fetchall()
        return result

    def remove_uptime(self, end):
        """
            Remove all uptimes less than a specified value
        :param end: Value to end at for uptime removal
        """
        query = f"DELETE FROM {self._schema}.uptime WHERE time < %s"
        self._cursor.execute(query, [end])
