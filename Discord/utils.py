"""
    Holds utility class and special subclasses for Talos.

    author: CraftSpider
"""

import inspect
import itertools
import math
import re
import discord
import logging
import aiohttp
import abc
import mysql.connector.abstracts as mysql_abstracts
import discord.ext.commands as dcommands
import datetime as dt


log = logging.getLogger("talos.utils")

# Default priority levels
_levels = {
    "guild": 10,
    "channel": 20,
    "role": 30,
    "user": 40
}

# Special transforms
fullwidth_transform = {
    "!": "！", "\"": "＂", "#": "＃", "$": "＄", "%": "％", "&": "＆", "'": "＇", "(": "（", ")": "）", "*": "＊",
    "+": "＋", ",": "，", "-": "－", ".": "．", "/": "／", "0": "０", "1": "１", "2": "２", "3": "３", "4": "４",
    "5": "５", "6": "６", "7": "７", "8": "８", "9": "９", ":": "：", ";": "；", "<": "＜", "=": "＝", ">": "＞",
    "?": "？", "@": "＠", "A": "Ａ", "B": "Ｂ", "C": "Ｃ", "D": "Ｄ", "E": "Ｅ", "F": "Ｆ", "G": "Ｇ", "H": "Ｈ",
    "I": "Ｉ", "J": "Ｊ", "K": "Ｋ", "L": "Ｌ", "M": "Ｍ", "N": "Ｎ", "O": "Ｏ", "P": "Ｐ", "Q": "Ｑ", "R": "Ｒ",
    "S": "Ｓ", "T": "Ｔ", "U": "Ｕ", "V": "Ｖ", "W": "Ｗ", "X": "Ｘ", "Y": "Ｙ", "Z": "Ｚ", "[": "［", "\\": "＼",
    "]": "］", "^": "＾", "_": "＿", "`": "｀", "a": "ａ", "b": "ｂ", "c": "ｃ", "d": "ｄ", "e": "ｅ", "f": "ｆ",
    "g": "ｇ", "h": "ｈ", "i": "ｉ", "j": "ｊ", "k": "ｋ", "l": "ｌ", "m": "ｍ", "n": "ｎ", "o": "ｏ", "p": "ｐ",
    "q": "ｑ", "r": "ｒ", "s": "ｓ", "t": "ｔ", "u": "ｕ", "v": "ｖ", "w": "ｗ", "x": "ｘ", "y": "ｙ", "z": "ｚ",
    "{": "｛", "|": "｜", "}": "｝", "~": "～", " ": "　"
}


class NotRegistered(dcommands.CommandError):
    """Error raised when a Talos command requires a registered user, and the given user isn't."""
    def __init__(self, message, *args):
        if type(message) == discord.Member or type(message) == discord.User:
            message = str(message)
        super().__init__(message, *args)

# Fundamental Talos classes


class EmbedPaginator:
    """Does fancy embed paginating. Will make a single embed with all given fields, except if it becomes too long.
    A single field being too long becomes Field, Field continued. A whole embed then each field becomes its own embed.
    """

    __slots__ = ["max_size", "title", "description", "fields", "footer", "pages", "colours", "colour_pos"]

    MAX_TOTAL = 6000
    MAX_TITLE = 256
    MAX_DESCRIPTION = 2048
    MAX_FIELDS = 25
    MAX_FIELD_NAME = 256
    MAX_FIELD_VALUE = 1024
    MAX_FOOTER = 2048
    MAX_AUTHOR = 256

    def __init__(self, max_size: int=MAX_TOTAL, colour=discord.Colour(0x000000)):
        self.max_size = max_size
        self.title = ""
        self.description = ""
        self.fields = []
        self.footer = "Page {0}/{1}"
        self.pages = []
        self.colour_pos = 0
        if isinstance(colour, (list, tuple)):
            self.colours = colour
        else:
            self.colours = [colour]

    @property
    def size(self):
        """The current size of the embed paginator. A somewhat complex value, based on total pages and such."""
        size = len(self.title) + len(self.description.rstrip())
        for field in self.fields:
            title = len(field[0])
            value = len(field[1])
            size += title + value
            if value > self.MAX_FIELD_VALUE:
                size += (title + 6)*(value//1024)
        # Ignore this mess (for calculating footer size, which will depend on number of pages)
        old_size = size
        cur_pages = int(math.ceil(size/self.max_size)) if size > 0 else 1
        for i in range(cur_pages):
            size += len(self.footer.format(i, cur_pages))
        while cur_pages != (int(math.ceil(size/self.max_size)) if size > 0 else 1):
            cur_pages = int(math.ceil(size/self.max_size))
            size = old_size
            for i in range(cur_pages):
                size += len(self.footer.format(i, cur_pages))

        return size

    @property
    def page_number(self):
        """The number of pages in the embed, in other words, the minimum number of embeds to fit the content."""
        size = self.size
        return math.ceil(size / self.max_size) if size > 0 else 1

    def _next_colour(self):
        """Gets the next colour in the colour queue. Queue loops."""
        colour = self.colours[self.colour_pos]
        self.colour_pos = (self.colour_pos + 1) % len(self.colours)
        return colour

    @property
    def real_fields(self):
        """Gets the actual number of fields in the embed, given fields split on max length."""
        out = []
        for field in self.fields:
            if len(field[1]) > self.MAX_FIELD_VALUE:
                for i in range(int(math.ceil(len(field[1])/self.MAX_FIELD_VALUE))):
                    if i == 0:
                        out.append([field[0], field[1][0:self.MAX_FIELD_VALUE+1], field[2]])
                    else:
                        out.append([field[0] + " cont.",
                                    field[1][i*self.MAX_FIELD_VALUE+1:(i+1)*self.MAX_FIELD_VALUE+1], field[2]])
            else:
                out.append([field[0], field[1], field[2]])
        return out

    def set_title(self, title: str):
        """Sets the embed title. Title length must be less than MAX_TITLE"""
        if len(title) > self.MAX_TITLE:
            raise ValueError("Title length must be less than or equal to {}".format(self.MAX_TITLE))
        self.title = title
        return self

    def set_description(self, description: str):
        """Sets the embed description. Description length must be less than MAX_DESCRIPTION"""
        if len(description) > self.MAX_DESCRIPTION:
            raise ValueError("Description length must be less than or equal to {}".format(self.MAX_DESCRIPTION))
        self.description = description
        return self

    def set_footer(self, footer: str):
        """Sets the embed footer. Footer length must be less than MAX_FOOTER"""
        if len(footer) > self.MAX_FOOTER:
            raise ValueError("Footer length must be less than or equal to {}".format(self.MAX_FOOTER))
        self.footer = footer
        return self

    def add_field(self, title: str, value: str, inline: bool=False):
        """Adds an embed field. Title length must be less than MAX_FIELD_NAMe"""
        if len(title) > self.MAX_FIELD_NAME:
            raise ValueError("Field title length must be less than or equal to {}".format(self.MAX_FIELD_NAME))
        self.fields.append([title, value, inline])
        return self

    def close_pages(self):
        """Closes the embed, and builds the self.pages variable. If subsequent changes are made, must be re-called."""
        out = []
        if self.page_number == 1:
            embed = discord.Embed(title=self.title, description=self.description, colour=self._next_colour())
            real_fields = self.real_fields
            if len(real_fields) > self.MAX_FIELDS:
                for i in range(len(real_fields)):
                    field = real_fields[i]
                    if i % 25 == 0:
                        embed.set_footer(text=self.footer.format(math.ceil(i/25), self.page_number))
                        out.append(embed)
                        embed = discord.Embed(colour=self._next_colour())
                    embed.add_field(name=field[0], value=field[1], inline=field[2])
                self.pages = out
            else:
                for field in real_fields:
                    embed.add_field(name=field[0], value=field[1], inline=field[2])
                embed.set_footer(text=self.footer.format(self.page_number, self.page_number))
                out.append(embed)
                self.pages = out
        else:
            # TODO
            return discord.Embed(title="Not Implemented Yet",
                                 description="Please contact admins if this is not an expected result")


class TalosFormatter(dcommands.HelpFormatter):

    def __init__(self):
        self._paginator = None
        super().__init__(width=75)

    @property
    async def clean_prefix(self):
        return (await self.context.bot.get_prefix(self.context))[0]

    async def get_command_signature(self):
        """Retrieves the signature portion of the help page."""
        prefix = await self.clean_prefix
        cmd = self.command
        return prefix + cmd.signature

    async def get_ending_note(self):
        command_name = self.context.invoked_with
        return "Type {0}{1} command for more info on a command.\n" \
               "You can also type {0}{1} category for more info on a category.".format(
                   await self.clean_prefix, command_name
               )

    @staticmethod
    def capital_split(text: str):
        out = ""
        for char in text:
            if char.isupper():
                out += " {}".format(char)
            else:
                out += char
        return out.strip(" ")

    def embed_shorten(self, text: str):
        if len(text) > self.width:
            return text[:self.width - 3] + '...\n'
        return text

    def _subcommands_field_value(self, commands):
        out = ""
        for name, command in commands:
            if name in command.aliases:
                # skip aliases
                continue

            entry = '{0} - {1}\n'.format(name, command.description if command.description else "")
            shortened = self.embed_shorten(entry)
            out += shortened
        return out

    async def format(self):
        if self.context.bot.should_embed(self.context):
            return await self.embed_format()
        else:
            return await self.string_format()

    async def embed_format(self):
        self._paginator = EmbedPaginator()

        description = self.command.description if not self.is_cog() else inspect.getdoc(self.command)

        if description:
            # <description> section
            self._paginator.set_description(description)

        if isinstance(self.command, dcommands.Command):
            # <signature> section
            signature = await self.get_command_signature()
            self._paginator.add_field("Signature", signature)

            # <long doc> section
            if self.command.help:
                self._paginator.add_field("Documentation", self.command.help)

            if not self.has_subcommands():
                self._paginator.close_pages()
                return self._paginator.pages

        def category(tup):
            cog = tup[1].cog_name
            # we insert the zero width space there to give it approximate
            # last place sorting position.
            return self.capital_split(cog) + ':' if cog is not None else '\u200bBase Commands:'

        filtered = await self.filter_command_list()
        if self.is_bot():
            self._paginator.set_title("Talos Help")
            self._paginator.set_description(description+"\n"+await self.get_ending_note())

            data = sorted(filtered, key=category)
            for category, commands in itertools.groupby(data, key=category):
                commands = sorted(commands)
                title = None
                if len(commands) > 0:
                    title = category
                if title:
                    value = self._subcommands_field_value(commands)
                    self._paginator.add_field(title, value)
        else:
            filtered = sorted(filtered)
            if filtered:
                value = self._subcommands_field_value(filtered)
                self._paginator.add_field('Commands', value)

        self._paginator.close_pages()
        return self._paginator.pages

    async def string_format(self):
        self._paginator = dcommands.Paginator()

        # we need a padding of ~80 or so

        description = self.command.description if not self.is_cog() else inspect.getdoc(self.command)

        if description:
            # <description> portion
            self._paginator.add_line(description, empty=True)

        if isinstance(self.command, dcommands.Command):
            # <signature portion>
            signature = await self.get_command_signature()
            self._paginator.add_line(signature, empty=True)

            # <long doc> section
            if self.command.help:
                self._paginator.add_line(self.command.help, empty=True)

            # end it here if it's just a regular command
            if not self.has_subcommands():
                self._paginator.close_page()
                return self._paginator.pages

        max_width = self.max_name_size

        def category(tup):
            cog = tup[1].cog_name
            # we insert the zero width space there to give it approximate
            # last place sorting position.
            return self.capital_split(cog) + ':' if cog is not None else '\u200bBase Commands:'

        filtered = await self.filter_command_list()
        if self.is_bot():
            data = sorted(filtered, key=category)
            for category, commands in itertools.groupby(data, key=category):
                # there simply is no prettier way of doing this.
                commands = sorted(commands)
                if len(commands) > 0:
                    self._paginator.add_line(category)

                self._add_subcommands_to_page(max_width, commands)
        else:
            filtered = sorted(filtered)
            if filtered:
                self._paginator.add_line('Commands:')
                self._add_subcommands_to_page(max_width, filtered)

        # add the ending note
        self._paginator.add_line()
        ending_note = await self.get_ending_note()
        self._paginator.add_line(ending_note)
        return self._paginator.pages


class EmptyCursor(mysql_abstracts.MySQLCursorAbstract):

    DEFAULT_ONE = None
    DEFAULT_ALL = list()

    def __init__(self):
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


class TalosDatabase:

    def __init__(self, sql_conn):
        if sql_conn is not None:
            self._sql_conn = sql_conn
            self._cursor = sql_conn.cursor()
        else:
            self._sql_conn = None
            self._cursor = EmptyCursor()

    async def commit(self):
        """Commits all changes to the database"""
        log.debug("Committing data")
        self._sql_conn.commit()

    def is_connected(self):
        return self._sql_conn is not None and not isinstance(self._cursor, EmptyCursor)

    def raw_exec(self, statement):
        self._cursor.execute(statement)
        return self._cursor.fetchall()

    # Meta methods

    def get_column_type(self, table_name: str, column_name: str):
        if re.match("[^a-zA-Z0-9_-]", table_name) or re.match("[^a-zA-Z0-9_-]", column_name):
            raise ValueError("SQL Injection Detected!")
        query = "SELECT DATA_TYPE FROM information_schema.COLUMNS WHERE TABLE_NAME = %s AND COLUMN_NAME = %s"
        self._cursor.execute(query, [table_name, column_name])
        result = self._cursor.fetchone()
        if result is not None:
            result = result[0]
        return result

    def get_columns(self, table_name: str):
        if re.match("[^a-zA-Z0-9_-]", table_name):
            raise ValueError("SQL Injection Detected!")
        query = "SELECT COLUMN_NAME, DATA_TYPE FROM information_schema.COLUMNS WHERE TABLE_NAME = %s"
        self._cursor.execute(query, [table_name])
        return self._cursor.fetchall()

    # Guild option methods

    def get_guild_default(self, option_name: str):
        """Get the default value of an option"""
        if re.match("[^a-zA-Z0-9_-]", option_name):
            raise ValueError("SQL Injection Detected!")
        query = "SELECT {} FROM guild_options WHERE guild_id = -1".format(option_name)
        self._cursor.execute(query)
        result = self._cursor.fetchone()
        if result:
            return result[0]
        else:
            raise KeyError

    def get_guild_defaults(self):
        query = "SELECT * FROM guild_options WHERE guild_id = -1"
        self._cursor.execute(query)
        result = self._cursor.fetchone()
        if isinstance(result, (tuple, list)):
            return result
        elif result:
            return [result]
        else:
            return []

    def get_guild_option(self, guild_id: int, option_name: str):
        if re.match("[^a-zA-Z0-9_-]", option_name):
            raise ValueError("SQL Injection Detected!")
        query = "SELECT {} FROM guild_options WHERE guild_id = %s".format(option_name)
        self._cursor.execute(query, [guild_id])
        result = self._cursor.fetchone()
        if result is None or result[0] is None:
            result = self.get_guild_default(option_name)
        else:
            result = result[0]
        return result

    def get_guild_options(self, guild_id: int):
        query = "SELECT * FROM guild_options WHERE guild_id = %s"
        self._cursor.execute(query, [guild_id])
        result = self._cursor.fetchone()
        out = []
        if result is None:
            out = self.get_guild_defaults()
        else:
            rows = self.get_columns("guild_options")
            for item in range(len(result)):
                if result[item] is None:
                    out.append(self.get_guild_default(rows[item][0]))
                else:
                    out.append(result[item])
        return out

    def get_all_guild_options(self):
        query = "SELECT * FROM guild_options"
        self._cursor.execute(query)
        out = []
        for row in self._cursor:
            out.append(row)
        return out

    def set_guild_option(self, guild_id: int, option_name: str, value):
        if re.match("[^a-zA-Z0-9_-]", option_name):
            raise ValueError("SQL Injection Detected!")
        query = "INSERT INTO guild_options (guild_id, {0}) VALUES (%s, %s) "\
                "ON DUPLICATE KEY UPDATE "\
                "{0} = VALUES({0})".format(option_name)
        self._cursor.execute(query, [guild_id, value])

    def remove_guild_option(self, guild_id: int, option_name: str):
        if re.match("[^a-zA-Z0-9_-]", option_name):
            raise ValueError("SQL Injection Detected!")
        query = "UPDATE guild_options SET {} = null WHERE guild_id = %s".format(option_name)
        self._cursor.execute(query, [guild_id])

    # User option methods

    def get_user_default(self, option_name: str):
        if re.match("[^a-zA-Z0-9_-]", option_name):
            raise ValueError("SQL Injection Detected!")
        query = "SELECT {} FROM user_options WHERE user_id = -1".format(option_name)
        self._cursor.execute(query)
        result = self._cursor.fetchone()
        if result:
            return result[0]
        else:
            raise KeyError

    def get_user_defaults(self):
        query = "SELECT * FROM user_options WHERE user_id = -1"
        self._cursor.execute(query)
        result = self._cursor.fetchone()
        if isinstance(result, (tuple, list)):
            return result
        elif result:
            return [result]
        else:
            return []

    def get_user_option(self, user_id: int, option_name: str):
        if re.match("[^a-zA-Z0-9_-]", option_name):
            raise ValueError("SQL Injection Detected!")
        query = "SELECT {} FROM user_options WHERE user_id = %s".format(option_name)
        self._cursor.execute(query, [user_id])
        result = self._cursor.fetchone()
        if result is None or result[0] is None:
            result = self.get_user_default(option_name)
        else:
            result = result[0]
        return result

    def get_user_options(self, user_id: int):
        query = "SELECT * FROM user_options WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        result = self._cursor.fetchone()
        out = []
        if result is None:
            out = self.get_user_defaults()
        else:
            rows = self.get_columns("user_options")
            for item in range(len(result)):
                if result[item] is None:
                    out.append(self.get_user_default(rows[item][0]))
                else:
                    out.append(result[item])
        return out

    def get_all_user_options(self):
        query = "SELECT * FROM user_options"
        self._cursor.execute(query)
        out = []
        for row in self._cursor:
            out.append(row)
        return out

    def set_user_option(self, user_id: int, option_name: str, value):
        if re.match("[^a-zA-Z0-9_-]", option_name):
            raise ValueError("SQL Injection Detected!")
        query = "INSERT INTO user_options (user_id, {0}) VALUES (%s, %s) "\
                "ON DUPLICATE KEY UPDATE "\
                "{0} = VALUES({0})".format(option_name)
        self._cursor.execute(query, [user_id, value])

    def remove_user_option(self, user_id: int, option_name: str):
        if re.match("[^a-zA-Z0-9_-]", option_name):
            raise ValueError("SQL Injection Detected!")
        query = "UPDATE user_options SET {} = null WHERE user_id = %s".format(option_name)
        self._cursor.execute(query, [user_id])

    # User profile methods

    def register_user(self, user_id: int):
        query = "INSERT INTO user_options (user_id) VALUES (%s)"
        self._cursor.execute(query, [user_id])
        query = "INSERT INTO user_profiles (user_id) VALUES (%s)"
        self._cursor.execute(query, [user_id])

    def deregister_user(self, user_id: int):
        query = "DELETE FROM user_options WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        query = "DELETE FROM user_profiles WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        query = "DELETE FROM invoked_commands WHERE user_id = %s"
        self._cursor.execute(query, [user_id])

    def get_user(self, user_id: int):
        query = "SELECT * FROM user_profiles WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        return self._cursor.fetchone()

    def get_description(self, user_id: int):
        query = "SELECT description FROM user_profiles WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        return self._cursor.fetchone()

    def set_description(self, user_id: int, desc: str):
        query = "UPDATE user_profiles SET description = %s WHERE user_id = %s"
        self._cursor.execute(query, [desc, user_id])

    def get_title(self, user_id: int):
        query = "SELECT title FROM user_profiles WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        return self._cursor.fetchone()

    def set_title(self, user_id: int, title: str):
        query = "UPDATE user_profiles SET title = %s WHERE user_id = %s"
        self._cursor.execute(query, [title, user_id])

    def user_invoked_command(self, user_id: int, command: str):
        query = "UPDATE user_profiles SET commands_invoked = commands_invoked + 1 WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        query = "INSERT INTO invoked_commands (user_id, command_name) VALUES (%s, %s) " \
                "ON DUPLICATE KEY UPDATE " \
                "times_invoked = times_invoked + 1"
        self._cursor.execute(query, [user_id, command])

    def get_command_data(self, user_id: int):
        query = "SELECT command_name, times_invoked FROM invoked_commands WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        return self._cursor.fetchall()

    def get_favorite_command(self, user_id: int):
        query = "SELECT command_name, times_invoked FROM invoked_commands WHERE user_id = %s " \
                "ORDER BY times_invoked DESC LIMIT 1"
        self._cursor.execute(query, [user_id])
        return self._cursor.fetchone()

    # Ops methods

    def get_all_ops(self):
        query = "SELECT guild_id, opname FROM ops"
        self._cursor.execute(query)
        out = []
        for row in self._cursor:
            out.append(row)
        return out

    def get_ops(self, guild_id: int):
        query = "SELECT opname FROM ops WHERE guild_id = %s"
        self._cursor.execute(query, [guild_id])
        out = []
        for row in self._cursor:
            out.append(row[0])
        return out

    def add_op(self, guild_id: int, opname: str):
        query = "INSERT INTO ops VALUES (%s, %s)"
        self._cursor.execute(query, [guild_id, opname])

    def remove_op(self, guild_id: int, opname: str):
        query = "DELETE FROM ops WHERE guild_id = %s AND opname = %s"
        self._cursor.execute(query, [guild_id, opname])

    # Perms methods

    def get_perm_rule(self, guild_id: int, command: str, perm_type: str, target: str):
        query = "SELECT priority, allow FROM perm_rules WHERE guild_id = %s AND command = %s AND perm_type = %s AND"\
                " target = %s"
        self._cursor.execute(query, [guild_id, command, perm_type, target])
        return self._cursor.fetchone()

    def get_perm_rules(self, guild_id: int=-1, command=None, perm_type=None, target=None):
        query = "SELECT command, perm_type, target, priority, allow FROM perm_rules WHERE guild_id = %s"
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
        return self._cursor.fetchall()

    def get_all_perm_rules(self):
        query = "SELECT guild_id, command, perm_type, target, priority, allow FROM perm_rules"
        self._cursor.execute(query)
        return self._cursor.fetchall()

    def set_perm_rule(self, guild_id: int, command: str, perm_type: str, allow: bool, priority=None, target=None):
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

    # Uptime methods

    def add_uptime(self, uptime):
        query = "INSERT INTO uptime VALUES (%s)"
        self._cursor.execute(query, [uptime])

    def get_uptime(self, start):
        query = "SELECT time FROM uptime WHERE time >= %s"
        self._cursor.execute(query, [start])
        result = self._cursor.fetchall()
        return result

    def remove_uptime(self, end):
        query = "DELETE FROM uptime WHERE time < %s"
        self._cursor.execute(query, [end])


class TalosHTTPClient(aiohttp.ClientSession):

    NANO_URL = "https://nanowrimo.org/"
    BTN_URL = "https://www.behindthename.com/"

    def __init__(self, *args, **kwargs):

        self.username = kwargs.pop("username", "")
        self.password = kwargs.pop("password", "")
        self.btn_key = kwargs.pop("btn_key", "")

        super().__init__(*args, **kwargs)

    async def get_site(self, url, **kwargs):
        async with self.get(url, **kwargs) as response:
            return await response.text()

    async def btn_get_names(self, gender="", usage="", number=1, surname=False):
        surname = "yes" if surname else "no"
        gender = "&gender="+gender if gender else gender
        usage = "&usage="+usage if usage else usage
        url = self.BTN_URL + "api/random.php?key={}&randomsurname={}&number={}{}{}".format(self.btn_key, surname,
                                                                                           number, gender, usage)
        async with self.get(url) as response:
            if response.status == 200:
                text = await response.text()
                return re.findall(r"<name>(.*?)</name>", text)
            else:
                log.warning("BTN returned {}".format(response.status))
                return None

    async def nano_get_user(self, username):
        """Returns a given NaNo user profile, if it can be found. If not, returns None"""
        async with self.get(self.NANO_URL + "participants/{}".format(username)) as response:
            if response.status == 200:
                if not str(response.url).startswith("https://nanowrimo.org/participants"):
                    return None
                return await response.text()
            elif response.status == 403:
                response = await self.nano_login_client()
                log.debug("Login Status: {}".format(response))
                return await self.nano_get_user(username)
            else:
                print(response.status)
                return None

    async def nano_get_novel(self, username, novel_name=""):
        if novel_name == "":
            user_page = await self.nano_get_user(username)
            if user_page is None:
                return None, None
            novel_name = re.search(r"<a href=\"/participants/{}/novels/(.*?)/stats\">".format(username), user_page)
            if novel_name is None:
                return None, None
            novel_name = novel_name.group(1)
        # Get novel page for return
        async with self.get(self.NANO_URL + "participants/{}/novels/{}".format(username, novel_name)) as response:
            if response.status == 200:
                if not str(response.url).startswith("https://nanowrimo.org/participants"):
                    return None, None
                novel_page = await response.text()
            elif response.status == 403:
                response = await self.nano_login_client()
                log.debug("Login Status: {}".format(response))
                return await self.nano_get_novel(username, novel_name)
            elif response.status == 404:
                return None, None
            else:
                log.warning("Got unexpected response status {}".format(response.status))
                return None, None
        # Get novel stats for return
        async with self.get(self.NANO_URL + "participants/{}/novels/{}/stats".format(username, novel_name)) as response:
            if response.status == 200:
                if not str(response.url).startswith("https://nanowrimo.org/participants"):
                    return None, None
                novel_stats = await response.text()
            elif response.status == 403:
                response = await self.nano_login_client()
                log.debug("Login Status: {}".format(response))
                return await self.nano_get_novel(username, novel_name)
            elif response.status == 404:
                return None, None
            else:
                log.warning("Got unexpected response status {}".format(response.status))
                return None, None
        return novel_page, novel_stats

    async def nano_login_client(self):
        login_page = await self.get_site(self.NANO_URL + "sign_in")
        pattern = re.compile("<input name=\"authenticity_token\" .*? value=\"(.*?)\" />")
        auth_key = pattern.search(login_page).group(1)
        params = {
            "utf8": "✓",
            "authenticity_token": auth_key,
            "user_session[name]": self.username,
            "user_session[password]": self.password,
            "user_session[remember_me]": "0",
            "commit": "Sign+in"
        }
        async with self.post(self.NANO_URL + "sign_in", data=params) as response:
            return response.status


def to_snake_case(text):
    out = ""
    for char in text:
        if char.isupper():
            out += "_{}".format(char.lower())
        else:
            out += char
    return out.strip("_")


def _perms_check(ctx):
    """Determine whether the person calling the command is allowed to run this command"""

    if isinstance(ctx.channel, discord.abc.PrivateChannel) or ctx.author.id in ctx.bot.ADMINS:
        return True
    command = str(ctx.command)

    try:
        if not ctx.bot.database.get_guild_option(ctx.guild.id, to_snake_case(ctx.command.instance.__class__.__name__)):
            return False
    except KeyError:
        pass
    perms = ctx.bot.database.get_perm_rules(ctx.guild.id, command)
    if len(perms) == 0:
        return True
    perms.sort(key=lambda x: x[3])
    for perm in perms:
        if perm[1] == "user" and perm[2] == str(ctx.author):
            return perm[4]
        elif perm[1] == "role":
            for role in ctx.author.roles:
                if perm[2] == str(role):
                    return perm[4]
        elif perm[1] == "channel" and perm[2] == str(ctx.channel):
            return perm[4]
        elif perm[1] == "guild":
            return perm[4]
    return True


class TalosCog:
    """Super class to all Talos cogs. Sets a default __local_check, and other init stuff."""

    __slots__ = ['bot', 'database', '__local_check']

    def __init__(self, bot):
        """Initiates the current cog. Takes an instance of Talos to use while running."""
        self.bot = bot
        self.database = None
        if hasattr(bot, "database"):
            self.database = bot.database
        if not hasattr(self, "_{0.__class__.__name__}__local_check".format(self)):
            setattr(self, "_{0.__class__.__name__}__local_check".format(self), _perms_check)


# Command classes

class PW:
    """Represents a Productivity War"""

    __slots__ = ['start', 'end', 'members']

    def __init__(self):
        """Creates a PW object, with empty variables."""
        self.start = None
        self.end = None
        self.members = []

    def get_started(self):
        """Gets whether the PW is started"""
        return self.start is not None

    def get_finished(self):
        """Gets whether the PW is ended"""
        return self.end is not None

    def begin(self):
        """Starts the PW, assumes it isn't started"""
        self.start = dt.datetime.utcnow()
        for member in self.members:
            if not member.get_started():
                member.begin(self.start)

    def finish(self):
        """Ends the PW, assumes it isn't ended"""
        self.end = dt.datetime.utcnow()
        for member in self.members:
            if not member.get_finished():
                member.finish(self.end)

    def join(self, member):
        """Have a new member join the PW."""
        if PWMember(member) not in self.members and self.get_finished() is not True:
            new_mem = PWMember(member)
            if self.get_started():
                new_mem.begin(dt.datetime.utcnow())
            self.members.append(new_mem)
            return True
        else:
            return False

    def leave(self, member):
        """Have a member in the PW leave the PW."""
        if PWMember(member) in self.members:
            for user in self.members:
                if user == PWMember(member):
                    if user.get_finished():
                        return 2
                    elif user.get_started():
                        user.finish(dt.datetime.utcnow())
                    else:
                        self.members.remove(user)
                        break
            # check if anyone isn't finished
            for user in self.members:
                if not user.get_finished():
                    return 0
            # if everyone is finished, end the pw
            self.finish()
            return 0
        else:
            return 1


class PWMember:
    """Represents a single member of a PW"""

    __slots__ = ['user', 'start', 'end']

    def __init__(self, user):
        self.user = user
        self.start = None
        self.end = None

    def __str__(self):
        return str(self.user)

    def __eq__(self, other):
        return isinstance(other, PWMember) and self.user == other.user

    def get_len(self):
        """Get the length of time this member was in the PW"""
        if self.end is None or self.start is None:
            return -1
        else:
            return self.end - self.start

    def get_started(self):
        """Get whether this member has started a PW"""
        return self.start is not None

    def get_finished(self):
        """Get whether this member has finished a PW"""
        return self.end is not None

    def begin(self, time):
        """Set this member as having started a PW"""
        if not isinstance(time, (dt.datetime, dt.time)):
            raise ValueError("Time must be a datetime or time instance")
        self.start = time.replace(microsecond=0)

    def finish(self, time):
        """Set this member as having finished a PW"""
        if not isinstance(time, (dt.datetime, dt.time)):
            raise ValueError("Time must be a datetime or time instance")
        self.end = time.replace(microsecond=0)
