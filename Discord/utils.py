"""
    Holds utility class and special subclasses for Talos.

    author: CraftSpider
"""

import asyncio
import inspect
import itertools
import math
import discord
import discord.ext.commands as dcommands
from datetime import datetime


# Fundamental Talos classes


class EmbedPaginator:
    """Does fancy embed paginating. Will make a single embed with all given fields, except if it becomes too long.
    A single field being too long becomes Field, Field continued. A whole embed then each field becomes its own embed.
    """

    __slots__ = ["max_size", "title", "description", "fields", "footer", "pages", "colour"]

    MAX_TOTAL = 6000
    MAX_TITLE = 256
    MAX_DESCRIPTION = 2048
    MAX_FIELDS = 25
    MAX_FIELD_NAME = 256
    MAX_FIELD_VALUE = 1024
    MAX_FOOTER = 2048
    MAX_AUTHOR = 256

    def __init__(self, max_size=0, colour=discord.Color(0x000000)):
        self.max_size = max_size if max_size > 0 else self.MAX_TOTAL
        self.title = ""
        self.description = ""
        self.fields = []
        self.footer = "Page {}/{}"
        self.pages = []
        if isinstance(colour, (list, tuple)):
            self.colour = colour
        else:
            self.colour = [colour]

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
        cur_pages = int(math.ceil(size/self.max_size))
        for i in range(cur_pages):
            size += len(self.footer.format(i, cur_pages))
        while cur_pages != int(math.ceil(size/self.max_size)):
            cur_pages = int(math.ceil(size/self.max_size))
            size = old_size
            for i in range(cur_pages):
                size += len(self.footer.format(i, cur_pages))

        return size

    @property
    def page_number(self):
        return math.ceil(self.size / self.max_size)

    def next_colour(self):
        colour = self.colour.pop(0)
        self.colour.append(colour)
        return colour

    @property
    def real_fields(self):
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
        if len(title) > self.MAX_TITLE:
            raise ValueError("Title length must be less than or equal to {}".format(self.MAX_TITLE))
        self.title = title
        return self

    def set_description(self, description: str):
        if len(description) > self.MAX_DESCRIPTION:
            raise ValueError("Description length must be less than or equal to {}".format(self.MAX_DESCRIPTION))
        self.description = description
        return self

    def set_footer(self, footer: str):
        if len(footer) > self.MAX_FOOTER:
            raise ValueError("Footer length must be less than or equal to {}".format(self.MAX_FOOTER))
        self.footer = footer
        return self

    def add_field(self, title, value, inline=False):
        if len(title) > self.MAX_FIELD_NAME:
            raise ValueError("Field title length must be less than or equal to {}".format(self.MAX_FIELD_NAME))
        self.fields.append([title, value, inline])
        return self

    def close_pages(self):
        out = []
        if self.page_number == 1:
            embed = discord.Embed(title=self.title, description=self.description, colour=self.next_colour())
            real_fields = self.real_fields
            if len(real_fields) > self.MAX_FIELDS:
                for i in range(len(real_fields)):
                    field = real_fields[i]
                    if i % 25 == 0:
                        embed.set_footer(text=self.footer.format(math.ceil(i/25), self.page_number))
                        out.append(embed)
                        embed = discord.Embed(colour=self.next_colour())
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
            return discord.Embed(title="Not Implemented Yet")


class TalosFormatter(dcommands.HelpFormatter):

    def __init__(self):
        self._paginator = None
        super().__init__(width=75)

    @property
    def clean_prefix(self):
        loop = asyncio.new_event_loop()
        future = loop.create_task(self.context.bot.get_prefix(self.context))
        loop.run_until_complete(future)
        return future.result()[0]

    @staticmethod
    def capital_split(text):
        out = ""
        for char in text:
            if char.isupper():
                out += " {}".format(char)
            else:
                out += char
        return out.strip(" ")

    def embed_shorten(self, text):
        if len(text) > self.width:
            return text[:self.width - 3] + '...\n'
        return text

    def _subcommands_field_value(self, commands):
        out = ""
        for name, command in commands:
            if name in command.aliases:
                # skip aliases
                continue

            entry = '{0} - {1}\n'.format(name, command.short_doc)
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
            signature = self.get_command_signature()
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
            self._paginator.set_description(description+"\n"+self.get_ending_note())

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
            signature = self.get_command_signature()
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
        ending_note = self.get_ending_note()
        self._paginator.add_line(ending_note)
        return self._paginator.pages


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
        self.start = datetime.utcnow()
        for member in self.members:
            if not member.get_started():
                member.begin(self.start)

    def finish(self):
        """Ends the PW, assumes it isn't ended"""
        self.end = datetime.utcnow()
        for member in self.members:
            if not member.get_finished():
                member.finish(self.end)

    def join(self, member):
        """Have a new member join the PW."""
        if PW_Member(member) not in self.members:
            new_mem = PW_Member(member)
            if self.get_started():
                new_mem.begin(datetime.utcnow())
            self.members.append(new_mem)
            return True
        else:
            return False

    def leave(self, member):
        """Have a member in the PW leave the PW."""
        if PW_Member(member) in self.members:
            for user in self.members:
                if user == PW_Member(member):
                    if user.get_finished():
                        return 2
                    else:
                        user.finish(datetime.utcnow())
            for user in self.members:
                if not user.get_finished():
                    return 0
            self.finish()
            return 0
        else:
            return 1


class PW_Member:
    """Represents a single member of a PW"""

    __slots__ = ['user', 'start', 'end']

    def __init__(self, user):
        self.user = user
        self.start = None
        self.end = None

    def __str__(self):
        return str(self.user)

    def __eq__(self, other):
        return isinstance(other, PW_Member) and self.user == other.user

    def get_len(self):
        if self.end is None or self.start is None:
            return -1
        else:
            return self.end - self.start

    def get_started(self):
        return self.start is not None

    def get_finished(self):
        return self.end is not None

    def begin(self, time):
        if not isinstance(time, (datetime, time)):
            raise ValueError("Time must be a datetime or time instance")
        self.start = time.replace(microsecond=0)

    def finish(self, time):
        if not isinstance(time, (datetime, time)):
            raise ValueError("Time must be a datetime or time instance")
        self.end = time.replace(microsecond=0)
