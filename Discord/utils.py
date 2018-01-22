"""
    Holds utility class and special subclasses for Talos.

    author: CraftSpider
"""
import inspect
import itertools
import math
import re
import io
import logging
import aiohttp
import paginators
import discord
import discord.ext.commands as dcommands
import mysql.connector.abstracts as mysql_abstracts
import datetime as dt


log = logging.getLogger("talos.utils")

# Default priority levels
_levels = {
    "guild": 10,
    "channel": 20,
    "role": 30,
    "user": 40
}

# Normal characters to fullwidth characters
fullwidth_transform = {
    "!": "！", "\"": "＂", "#": "＃", "$": "＄", "£": "￡", "%": "％", "&": "＆", "'": "＇", "(": "（", ")": "）",
    "*": "＊", "+": "＋", ",": "，", "-": "－", ".": "．", "/": "／", "0": "０", "1": "１", "2": "２", "3": "３",
    "4": "４", "5": "５", "6": "６", "7": "７", "8": "８", "9": "９", ":": "：", ";": "；", "<": "＜", "=": "＝",
    ">": "＞", "?": "？", "@": "＠", "A": "Ａ", "B": "Ｂ", "C": "Ｃ", "D": "Ｄ", "E": "Ｅ", "F": "Ｆ", "G": "Ｇ",
    "H": "Ｈ", "I": "Ｉ", "J": "Ｊ", "K": "Ｋ", "L": "Ｌ", "M": "Ｍ", "N": "Ｎ", "O": "Ｏ", "P": "Ｐ", "Q": "Ｑ",
    "R": "Ｒ", "S": "Ｓ", "T": "Ｔ", "U": "Ｕ", "V": "Ｖ", "W": "Ｗ", "X": "Ｘ", "Y": "Ｙ", "Z": "Ｚ", "[": "［",
    "\\": "＼", "]": "］", "^": "＾", "_": "＿", "`": "｀", "a": "ａ", "b": "ｂ", "c": "ｃ", "d": "ｄ", "e": "ｅ",
    "f": "ｆ", "g": "ｇ", "h": "ｈ", "i": "ｉ", "j": "ｊ", "k": "ｋ", "l": "ｌ", "m": "ｍ", "n": "ｎ", "o": "ｏ",
    "p": "ｐ", "q": "ｑ", "r": "ｒ", "s": "ｓ", "t": "ｔ", "u": "ｕ", "v": "ｖ", "w": "ｗ", "x": "ｘ", "y": "ｙ",
    "z": "ｚ", "{": "｛", "|": "｜", "¦": "￤", "}": "｝", "~": "～", "¬": "￢", "¢": "￠", " ": "　"
}

# Timezone names to timezone objects
tz_map = {
    "A": +1, "ACDT": +10.5, "ACST": +9.5, "ACT": None, "ACWST": +8.75, "ADT": -3, "AEDT": +11, "AEST": +10, "AET": None,
    "AFT": +4.5, "AKDT": -8, "AKST": -9, "ALMT": +6, "AMST": -3, "AMT": -4, "ANAST": +12, "ANAT": +12, "AQTT": +5,
    "ART": -3, "AST": -4, "AT": None, "AWDT": +9, "AWST": +8, "AZOST": 0, "AZOT": -1, "AZST": +5, "AZT": +4, "AoE": -12,
    "B": +2, "BNT": +8, "BOT": -4, "BRST": -2, "BRT": -3, "BST": +1, "BTT": +6, "C": +3, "CAST": +8, "CAT": +2,
    "CCT": +6.5, "CDT": -5, "CEST": +2, "CET": +1, "CHADT": +13.75, "CHAST": +12.45, "CHOST": +9, "CHOT": +8,
    "CHUT": +10, "CIDST": -4, "CIST": -5, "CKT": -10, "CLST": -3, "CLT": -4, "COT": -5, "CST": -6, "CT": None,
    "CVT": -1, "CXT": +7, "ChST": +10, "D": +4, "DAVT": +7, "DDUT": +10, "E": +5, "EASST": -5, "EAST": -6, "EAT": +3,
    "ECT": -5, "EDT": -4, "EEST": +3, "EET": +2, "EGST": 0, "EGT": -1, "EST": -5, "ET": None, "F": +6, "FET": +3,
    "FJST": +13, "FJT": +12, "FKST": -3, "FKT": -4, "FNT": -2, "G": +7, "GALT": -6, "GAMT": -9, "GET": +4, "GFT": -3,
    "GILT": +12, "GMT": 0, "GST": +4, "GYT": -4, "H": +8, "HADT": -9, "HAST": -10, "HKT": +8, "HOVST": +8, "HOVT": +7,
    "I": +9, "ICT": +7, "IDT": +3, "IOT": +6, "IRDT": +4.5, "IRKST": +9, "IRKT": +8, "IRST": +3.5, "IST": +1, "JST": +9,
    "K": +10, "KGT": +6, "KOST": +11, "KRAST": +8, "KRAT": +7, "KST": +9, "KUYT": +4, "L": +11, "LHDT": +11,
    "LHST": +10.5, "LINT": +14, "M": +12, "MAGST": +12, "MAGT": +11, "MART": -9.5, "MAWT": +5, "MDT": -6, "MHT": +12,
    "MMT": +6.5, "MSD": +4, "MSK": +3, "MST": -7, "MT": None, "MUT": +4, "MVT": +5, "MYT": +8, "N": -1, "NCT": +11,
    "NDT": -2.5, "NFT": +11, "NOVST": +7, "NOVT": +6, "NPT": +5.75, "NRT": +12, "NST": -3.5, "NUT": -11, "NZDT": +13,
    "NZST": +12, "O": -2, "OMSST": +7, "OMST": +6, "ORAT": +5, "P": -3, "PDT": -7, "PET": -5, "PETST": +12, "PETT": +12,
    "PGT": +10, "PHOT": +13, "PHT": +8, "PKT": +5, "PMDT": -2, "PMST": -3, "PONT": +11, "PST": -8, "PT": None,
    "PWT": +9, "PYST": -3, "PYT": +8.5, "Q": -4, "QYZT": +6, "R": -5, "RET": +4, "ROTT": -3, "S": -6, "SAKT": +11,
    "SAMT": +4, "SAST": +2, "SBT": +11, "SCT": +4, "SGT": +8, "SRET": +11, "SRT": -3, "SST": -11, "SYOT": +3, "T": -7,
    "TAHT": -10, "TFT": +5, "TJT": +5, "TKT": +13, "TLT": +9, "TMT": +5, "TOST": +14, "TOT": +13, "TRT": +3, "TVT": +12,
    "U": -8, "ULAST": +9, "ULAT": +8, "UTC": 0, "UYST": -2, "UYT": -3, "UZT": +5, "V": -9, "VET": -4, "VLAST": +11,
    "VLAT": +10, "VOST": +6, "VUT": +11, "W": -10, "WAKT": +12, "WARST": -3, "WAST": +2, "WAT": +1, "WEST": +1,
    "WET": 0, "WFT": +12, "WGST": -2, "WGT": -3, "WIB": +7, "WIT": +9, "WITA": +8, "WST": +14, "WT": 0, "X": -11,
    "Y": -12, "YAKST": +10, "YAKT": +9, "YAPT": +10, "YEKST": +6, "YEKT": +5, "Z": 0
}


# Talos errors

class NotRegistered(dcommands.CommandError):
    """Error raised when a Talos command requires a registered user, and the given user isn't."""
    def __init__(self, message, *args):
        if type(message) == discord.Member or type(message) == discord.User:
            message = str(message)
        super().__init__(message, *args)


class CustomCommandError(dcommands.CommandError):
    pass


# Fundamental Talos classes

class EmbedPaginator:

    __slots__ = ("_max_size", "_title", "_description", "_fields", "_footer", "_built_pages", "_colours", "_colour_pos",
                 "_closed", "_author", "_author_url", "_author_avatar", "repeat_title", "repeat_desc", "repeat_author",
                 "_timestamp", "_footer_url")

    MAX_TOTAL = 6000
    MAX_TITLE = 256
    MAX_DESCRIPTION = 2048
    MAX_FIELDS = 25
    MAX_FIELD_NAME = 256
    MAX_FIELD_VALUE = 1024
    MAX_FOOTER = 2048
    MAX_AUTHOR = 256

    def __init__(self, max_size=MAX_TOTAL, colour=discord.Colour(0x000000)):
        """
            Instantiate a new EmbedPaginator
        :param max_size: maximum size for the embed. Defaults to Discord max embed size
        :param colour: colour for the embeds. Can be a list for rotating colours.
        """
        # Set default configuration
        self.repeat_title = False
        self.repeat_desc = False
        self.repeat_author = False
        # Set empty data values
        self._max_size = max_size
        self._title = ""
        self._description = ""
        self._author = None
        self._author_url = discord.Embed.Empty
        self._author_avatar = discord.Embed.Empty
        self._fields = []
        self._timestamp = discord.Embed.Empty
        self._footer = "Page {0}/{1}"
        self._footer_url = discord.Embed.Empty
        self._built_pages = []
        self._colour_pos = 0
        self._closed = False
        if isinstance(colour, (list, tuple)):
            self._colours = colour
        else:
            self._colours = [colour]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @staticmethod
    def _suffix(d):
        """
            Determine the suffix for a date
        :param d: day to determine suffix of
        :return: string of suffix
        """
        return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')

    def _custom_strftime(self, strf, t):
        """
            Custom string-format function to allow a time format to contain day in the form `1st`, `2nd`, `3r`, etc.
        :param strf: Format string
        :param t: Time to format with the string
        :return: formatted string
        """
        return t.strftime(strf).replace('{D}', str(t.day) + self._suffix(t.day))

    @property
    def size(self):
        """
            The current size of the embed paginator. A somewhat complex value, based on total pages and such.
        :return: Length of the current embed given pages
        """
        # Base size
        size = len(self._title) + len(self._description)
        if self._author:
            size += len(self._author)
        # Add size for each field
        for field in self._fields:
            name = len(field[0])
            value = len(field[1])
            size += name + value
            # Add any extra title lengths for field overflow. value stays the same.
            if value > self.MAX_FIELD_VALUE:
                size += (name + 6)*(value//1024)
        # Calculate the size of things that are repeated on each page.
        pages = self.pages
        for i in range(pages):
            if self.repeat_title:
                size += len(self._title)
            if self.repeat_desc:
                size += len(self._description)
            if self.repeat_author and self._author:
                size += len(self._author)
            size += len(self._footer.format(i, pages))
            if self._timestamp != discord.Embed.Empty:
                size += len(self._custom_strftime("%a %b {D}, %Y at %I:%M %p", self._timestamp))
        # And that's the total size now.
        return size

    @property
    def pages(self):
        """
            The number of pages in the embed, in other words, the minimum number of embeds to fit the content.
        :return: The number of pages in the embed based on its size and fields.
        """
        max_pages = 10
        page = 1
        while math.floor(math.log(max_pages, 10)) != math.floor(math.log(page, 10)):
            max_pages = page
            page = 1
            cur_size = len(self._title) + len(self._description)
            if self._author:
                cur_size += len(self._author)
            for field in self._fields:
                field_size = len(field[0]) + len(field[1])
                footer_size = len(self._footer.format(page, max_pages))
                if cur_size + field_size + footer_size > self._max_size or field == ("", "", False):
                    page += 1
                    cur_size = (len(self._title) if self.repeat_title else 0) +\
                               (len(self._description) if self.repeat_desc else 0) +\
                               (len(self._author) if self.repeat_author and self._author else 0)
                cur_size += field_size
        if len(self._fields) > 0 and self._fields[-1] == ("", "", False):
            page -= 1
        return page

    def _next_colour(self):
        """
            Gets the next colour in the colour queue. Queue loops.
        :return: Colour for the next embed.
        """
        colour = self._colours[self._colour_pos]
        self._colour_pos = (self._colour_pos + 1) % len(self._colours)
        return colour

    def configure(self, **options):
        """
            Set configuration parameters for the Paginator. These will effect size and number of pages properties as
            you would expect.
        :param options: Possible configuration options for the Paginator.
        """
        self.repeat_title = options.get("repeat_title", self.repeat_title)
        self.repeat_desc = options.get("repeat_desc", self.repeat_desc)
        self.repeat_author = options.get("repeat_author", self.repeat_author)

    def set_title(self, title):
        """
            Sets the embed title. Title length must be less than MAX_TITLE. Any string of whitespace longer than one
            will be cut down to one space, and line will be stripped, as discord will do it on post anyways.
        :param title: Title to set for embed.
        :return: Self to allow chaining
        """
        if self._closed:
            raise RuntimeError("Paginator closed")
        if len(title) > self.MAX_TITLE:
            raise ValueError("Title length must be less than or equal to {}".format(self.MAX_TITLE))
        self._title = re.sub(r"\s+", " ", title).strip()
        return self

    def set_description(self, description):
        """
            Sets the embed description. Description length must be less than MAX_DESCRIPTION. Will be right-stripped,
            as discord will do it on post anyways.
        :param description: Description to set for embed.
        :return: Self to allow chaining
        """
        if self._closed:
            raise RuntimeError("Paginator closed")
        if len(description) > self.MAX_DESCRIPTION:
            raise ValueError("Description length must be less than or equal to {}".format(self.MAX_DESCRIPTION))
        self._description = description.rstrip()
        return self

    def set_author(self, name, *, url=discord.Embed.Empty, avatar=discord.Embed.Empty):
        """
            Sets the embed's author. URL and Avatar are optional. Author name will be stripped following title rules.
        :param name: Name of the author
        :param url: URL for the author
        :param avatar: Avatar of the author
        :return: Self to allow chaining
        """
        if len(name) > self.MAX_AUTHOR:
            raise ValueError("Author name length must be less than or equal to {}".format(self.MAX_AUTHOR))
        self._author = re.sub(r"\s+", " ", name).strip()
        self._author_url = url
        self._author_avatar = avatar
        return self

    def set_colour(self, colour):
        """
            Sets the embed colour. Can be either a single discord.Colour or a list of them.
        :param colour: colour of list of colours to use.
        :return: Self to allow chaining
        """
        if isinstance(colour, (list, tuple)):
            self._colours = colour
        else:
            self._colours = [colour]
        return self

    def set_timestamp(self, timestamp):
        """
            Sets the embed timestamp. Takes a datetime.datetime.
        :param timestamp: Timestamp to set for all embeds
        :return: Self to allow chaining
        """
        self._timestamp = timestamp
        return self

    def set_footer(self, text, icon_url=discord.Embed.Empty):
        """
            Sets the embed footer. Footer length must be less than MAX_FOOTER. {0} and {1} in footer will be replaced
            with current and max pages for each embed.
        :param text: Footer to set for embed.
        :param icon_url: URL for the footer icon.
        :return: Self to allow chaining
        """
        if self._closed:
            raise RuntimeError("Paginator closed")
        if len(text) > self.MAX_FOOTER:
            raise ValueError("Footer length must be less than or equal to {}".format(self.MAX_FOOTER))
        self._footer = text
        self._footer_url = icon_url
        return self

    def add_field(self, name, value, inline=False):
        """
            Adds an embed field. Title length must be less than MAX_FIELD_NAME, or MAX_FIELD_NAME - 6 if value is longer
            than MAX_FIELD_VALUE. Title and value will be trimmed like main title and description are, as discord will
            do it anyways.
        :param name: Title of the embed field
        :param value: Value of the embed field
        :param inline: Whether this is an inline field. Defaults to False.
        :return: Self to allow chaining
        """
        if self._closed:
            raise RuntimeError("Paginator closed")
        if len(name) == 0 or len(value) == 0:
            raise ValueError("Field and Value must have a length greater than 0")
        if len(name) > self.MAX_FIELD_NAME or\
                (len(value) > self.MAX_FIELD_VALUE and len(name) > self.MAX_FIELD_NAME - 6):
            raise ValueError("Field title length must be less than or equal to {}".format(self.MAX_FIELD_NAME))

        name, value = re.sub(r"\s+", " ", name).strip(), value.rstrip()
        if len(value) > self.MAX_FIELD_VALUE:
            for i in range(int(math.ceil(len(value)/self.MAX_FIELD_VALUE))):
                match = re.search(r"[\n.][^\n.]*?(?!\.)$", value[:self.MAX_FIELD_VALUE + 1])
                if match is not None:
                    self._fields.append((name, value[:match.start()], inline))
                    value = value[match.start():]
                else:
                    self._fields.append((name, value[:self.MAX_FIELD_VALUE + 1], inline))
                    value = value[self.MAX_FIELD_VALUE + 1:]
                if i == 0:
                    name = name + " cont."
        else:
            self._fields.append((name, value, inline))
        return self

    def close_page(self):
        """
            Sets it so the paginator will jump to the next embed at this point, however close it is to the max size of
            the current one.
        """
        self._fields.append(("", "", False))

    def close(self):
        """
            Closes the embed, and builds real pages from input data. No subsequent changes will be allowed, the
            paginator will raise an error then.
        """
        if self._closed:
            raise RuntimeError("Tried to close paginator twice.")
        self._closed = True
        max_pages = self.pages
        page = 1
        cur_len = 0
        cur_fields = 0
        embed = discord.Embed(title=self._title, description=self._description, colour=self._next_colour(),
                              timestamp=self._timestamp)
        if self._author is not None:
            embed.set_author(name=self._author, url=self._author_url, icon_url=self._author_avatar)
        for field in self._fields:
            field_len = len(field[0]) + len(field[1])
            footer_len = len(self._footer.format(page, max_pages))
            cur_fields += 1
            if cur_fields % 25 == 0 or field == ("", "", False) or cur_len + field_len + footer_len > self._max_size:
                embed.set_footer(text=self._footer.format(page, max_pages), icon_url=self._footer_url)
                self._built_pages.append(embed)
                cur_len = 0
                page += 1
                embed = discord.Embed(title=self._title if self.repeat_title else discord.Embed.Empty,
                                      description=self._description if self.repeat_desc else discord.Embed.Empty,
                                      colour=self._next_colour(), timestamp=self._timestamp)
                if self.repeat_author and self._author is not None:
                    embed.set_author(name=self._author, url=self._author_url, icon_url=self._author_avatar)
            cur_len += field_len
            if field != ("", "", False):
                embed.add_field(name=field[0], value=field[1], inline=field[2])
        if embed.title or embed.description or len(embed.fields) != 0 or len(self._built_pages) == 0:
            embed.set_footer(text=self._footer.format(max_pages, max_pages), icon_url=self._footer_url)
            self._built_pages.append(embed)

    def get_pages(self):
        """
            Gets the pages of a closed Paginator. If not closed, raises an EnvironmentError
        :return: Constructed embed pages.
        """
        if self._closed:
            return self._built_pages
        raise RuntimeError("Paginator not Closed")


class TalosFormatter(dcommands.HelpFormatter):
    """
        Talos help formatter. Fairly self explanatory.
    """

    def __init__(self):
        """
            Instantiate a new TalosFormatter object
        """
        self._paginator = None
        super().__init__(width=75)

    @property
    async def clean_prefix(self):
        """
            Returns the prefix from a context, cleaned up.
        :return: Clean prefix for the given context
        """
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

            entry = '{0} - {1}\n'.format(name, command.description if command.description else "")
            shortened = self.embed_shorten(entry)
            out += shortened
        return out

    def _add_subcommands_to_page(self, max_width, commands):
        for name, command in commands:
            if name in command.aliases:
                # skip aliases
                continue

            entry = '  {0:<{width}} {1}'.format(name, command.description if command.description else "",
                                                width=max_width)
            shortened = self.shorten(entry)
            self._paginator.add_line(shortened)

    async def format(self):
        if self.context.bot.should_embed(self.context):
            return await self.embed_format()
        else:
            return await self.string_format()

    async def embed_format(self):
        self._paginator = paginators.PaginatedEmbed()

        description = self.command.description if not self.is_cog() else inspect.getdoc(self.command)

        if description:
            # <description> section
            self._paginator.description = description

        if isinstance(self.command, dcommands.Command):
            # <signature> section
            signature = await self.get_command_signature()
            self._paginator.add_field(name="Signature", value=signature)

            # <long doc> section
            if self.command.help:
                self._paginator.add_field(name="Documentation", value=self.command.help)

            # end it here if it's just a regular command
            if not self.has_subcommands():
                self._paginator.close()
                return self._paginator.pages

        def category(tup):
            cog = tup[1].cog_name
            # we insert the zero width space there to give it approximate
            # last place sorting position.
            return self.capital_split(cog) + ':' if cog is not None else '\u200bBase Commands:'

        filtered = await self.filter_command_list()
        if self.is_bot():
            self._paginator.title = "Talos Help"
            self._paginator.description = description+"\n"+await self.get_ending_note()

            data = sorted(filtered, key=category)
            for category, commands in itertools.groupby(data, key=category):
                commands = sorted(commands)
                title = None
                if len(commands) > 0:
                    title = category
                if title:
                    value = self._subcommands_field_value(commands)
                    self._paginator.add_field(name=title, value=value)
        else:
            filtered = sorted(filtered)
            if filtered:
                value = self._subcommands_field_value(filtered)
                self._paginator.add_field(name='Commands', value=value)

        self._paginator.close()
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
talos_create_table = "CREATE TABLE `{}` ({}) ENGINE=InnoDB DEFAULT CHARSET=utf8".format("{}", "{}")
talos_add_column = "ALTER TABLE {} ADD COLUMN {}".format("{}", "{}")  # Makes pycharm not complain
talos_remove_column = "ALTER TABLE {} DROP COLUMN {}".format("{}", "{}")
talos_modify_column = "ALTER TABLE {} MODIFY COLUMN {}".format("{}", "{}")
talos_tables = {
    "guild_options": {
        "columns": ["`guild_id` bigint(20) NOT NULL", "`rich_embeds` tinyint(1) DEFAULT NULL",
                    "`fail_message` tinyint(1) DEFAULT NULL", "`pm_help` tinyint(1) DEFAULT NULL",
                    "`commands` tinyint(1) DEFAULT NULL", "`user_commands` tinyint(1) DEFAULT NULL",
                    "`joke_commands` tinyint(1) DEFAULT NULL", "`writing_prompts` tinyint(1) DEFAULT NULL",
                    "`prompts_channel` varchar(64) DEFAULT NULL", "`prefix` varchar(32) DEFAULT NULL",
                    "`timezone` varchar(5) DEFAULT NULL"],
        "primary": "PRIMARY KEY (`guild_id`)",
        "defaults": [(-1, True, False, False, True, True, True, False, "prompts", "^", "UTC")]
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
                            self._cursor.execute(talos_add_column.format(table, column_spec))
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
                for item in talos_tables:
                    if talos_tables[item].get("defaults") is not None:
                        for values in talos_tables[item]["defaults"]:
                            self._cursor.execute("REPLACE INTO {} VALUES {}".format(item, values))

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
        """
        log.debug("Committing data")
        if self._sql_conn:
            self._sql_conn.commit()

    def is_connected(self):
        """
            Checks whether we are currently connected to a database
        :return: Whether the connection exists and the cursor isn't an EmptyCursor.
        """
        return self._sql_conn is not None and not isinstance(self._cursor, EmptyCursor)

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
        :return: The type of the given column
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
        :return: List of column names and data types
        """
        query = "SELECT COLUMN_NAME, DATA_TYPE FROM information_schema.COLUMNS WHERE TABLE_NAME = %s"
        self._cursor.execute(query, [table_name])
        return self._cursor.fetchall()

    # Guild option methods

    def get_guild_default(self, option_name):
        """
            Gets the default value for a guild option
        :param option_name: Name of the option to retrieve
        :return: Option default value
        """
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
        """
            Get all default guild option values
        :return: List of guild option default values
        """
        query = "SELECT * FROM guild_options WHERE guild_id = -1"
        self._cursor.execute(query)
        result = self._cursor.fetchone()
        if isinstance(result, (tuple, list)):
            return result
        elif result:
            return [result]
        else:
            return []

    def get_guild_option(self, guild_id, option_name):
        """
            Get an option for a guild. If option isn't set, gets the default for that option.
        :param guild_id: id of the guild to fetch option of
        :param option_name: name of the option to fetch
        :return: the set option value
        """
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

    def get_guild_options(self, guild_id):
        """
            Get all options for a guild. If option isn't set, returns the default for that option
        :param guild_id: id of the guild to get options of
        :return: list of the guild's options
        """
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
        """
            Get all options for all guilds.
        :return: List of all options of all guilds
        """
        query = "SELECT * FROM guild_options"
        self._cursor.execute(query)
        out = []
        for row in self._cursor:
            out.append(row)
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

    def get_user_default(self, option_name):
        """
            Gets the default value for a user option
        :param option_name: Name of the option to retrieve
        :return: Option default value
        """
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
        """
            Get all default user option values
        :return: List of user option default values
        """
        query = "SELECT * FROM user_options WHERE user_id = -1"
        self._cursor.execute(query)
        result = self._cursor.fetchone()
        if isinstance(result, (tuple, list)):
            return result
        elif result:
            return [result]
        else:
            return []

    def get_user_option(self, user_id, option_name):
        """
            Get an option for a user. If option isn't set, gets the default for that option.
        :param user_id: id of the user to fetch option of
        :param option_name: name of the option to fetch
        :return: the set option value
        """
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

    def get_user_options(self, user_id):
        """
            Get all options for a user. If option isn't set, returns the default for that option
        :param user_id: id of the user to get options of
        :return: list of the user's options
        """
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
        """
            Get all options for all users.
        :return: List of all options of all users
        """
        query = "SELECT * FROM user_options"
        self._cursor.execute(query)
        out = []
        for row in self._cursor:
            out.append(row)
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
            Return the whole profile object for a registered user
        :param user_id: id of the user to get profile of
        :return: Tuple of the user's profile in the database, or None.
        """
        query = "SELECT * FROM user_profiles WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        return self._cursor.fetchone()

    def get_description(self, user_id):
        """
            Get the description of a user
        :param user_id: id of the user to get description from
        :return: User description or None
        """
        query = "SELECT description FROM user_profiles WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        result = self._cursor.fetchone()
        if result:
            return result[0]
        else:
            return result

    def set_description(self, user_id, desc):
        """
            Set the description of a user
        :param user_id: id of the user to set the description of
        :param desc: thing to set description to
        """
        query = "UPDATE user_profiles SET description = %s WHERE user_id = %s"
        self._cursor.execute(query, [desc, user_id])

    def get_title(self, user_id):
        """
            Get the title of a user
        :param user_id: id of the user to get the title of
        :return: the title of the user or none
        """
        query = "SELECT title FROM user_profiles WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        result = self._cursor.fetchone()
        if result:
            return result[0]
        else:
            return result

    def set_title(self, user_id, title):
        """
            Set the title of a user
        :param user_id: id of the user to set the title for
        :param title: the title to set for the user
        """
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

    def get_command_data(self, user_id):
        """
            Get all data from invoked_commands for a specific user
        :param user_id: id of the user to grab the data of
        :return: List of commands to times invoked
        """
        query = "SELECT command_name, times_invoked FROM invoked_commands WHERE user_id = %s"
        self._cursor.execute(query, [user_id])
        return self._cursor.fetchall()

    def get_favorite_command(self, user_id):
        """
            Get the command a specific user has invoked the most.
        :param user_id: id of the user to get favorite command of
        :return: Favorite command for that user.
        """
        query = "SELECT command_name, times_invoked FROM invoked_commands WHERE user_id = %s " \
                "ORDER BY times_invoked DESC LIMIT 1"
        self._cursor.execute(query, [user_id])
        return self._cursor.fetchone()

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
        query = "SELECT priority, allow FROM perm_rules WHERE guild_id = %s AND command = %s AND perm_type = %s AND"\
                " target = %s"
        self._cursor.execute(query, [guild_id, command, perm_type, target])
        return self._cursor.fetchone()

    def get_perm_rules(self, guild_id=-1, command=None, perm_type=None, target=None):
        """
            Get a list of permissions rules for a variably specific context
        :param guild_id: id of the guild to get permissions for. If None, get default rules if they exist
        :param command: name of the command to get rules for. Any command if none.
        :param perm_type: type of permissions to get. Any type if none.
        :param target: target of permissions to get. Any target if none.
        :return: List of rules fitting the context.
        """
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


class TalosHTTPClient(aiohttp.ClientSession):

    NANO_URL = "https://nanowrimo.org/"
    BTN_URL = "https://www.behindthename.com/"
    CAT_URL = "https://thecatapi.com/api/"

    def __init__(self, *args, **kwargs):
        """
            Create a Talos HTTP Client object
        :param args: arguments to pass on
        :param kwargs: keyword args to use and pass on
        """
        self.username = kwargs.pop("username", "")
        self.password = kwargs.pop("password", "")
        self.btn_key = kwargs.pop("btn_key", "")
        self.cat_key = kwargs.pop("cat_key", "")

        super().__init__(*args, **kwargs)

    async def get_site(self, url, **kwargs):
        """
            Get the text of a given URL
        :param url: url to get text from
        :param kwargs: keyword args to pass to the GET call
        :return: text of the requested page
        """
        async with self.get(url, **kwargs) as response:
            return await response.text()

    async def btn_get_names(self, gender="", usage="", number=1, surname=False):
        """
            Get names from Behind The Name
        :param gender: gender to restrict names to. m or f
        :param usage: usage to restrict names to. eng for english, see documentation
        :param number: number of names to generate. Between 1 and 6.
        :param surname: whether to generate a random surname. Yes or No
        :return: List of names generated or None if failed
        """
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
        """
            Returns a given NaNo user profile, if it can be found.
        :param username: username of nano user to get profile of
        :return: text of the profile page for that user or None
        """
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
        """
            Returns the novel of a given NaNo user. This year's novel, if specific name not given.
        :param username: user to get novel of.
        :param novel_name: novel to get for user. Most recent if not given.
        :return: novel main page and novel stats page, or None None.
        """
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
        """
            Login the client to the NaNo site.
        :return: status of login request.
        """
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

    async def get_cat_pic(self):
        """
            Get a random cat picture from The Cat API
        :return: A discord.File with a picture of a cat.
        """
        async with self.get(self.CAT_URL + "images/get?api_key={}&type=jpg,png".format(self.cat_key)) as response:
            filename = ""
            if response.content_type == "image/jpeg":
                filename = "cat.jpeg"
            elif response.content_type == "image/png":
                filename = "cat.png"
            picture_data = await response.read()
            if not picture_data:
                return self.get_cat_pic()
            file = discord.File(io.BytesIO(picture_data), filename)
        return file


def to_snake_case(text):
    """
        Convert a string into snake case
    :param text: string to convert
    :return: string in snake case form
    """
    out = ""
    for char in text:
        if char.isupper():
            out += "_{}".format(char.lower())
        else:
            out += char
    return out.strip("_")


def _perms_check(ctx):
    """
        Determine whether the command can is allowed to run in this context.
    :param ctx: dcommands.Context object to consider
    :return: whether the command can run
    """
    if isinstance(ctx.channel, discord.abc.PrivateChannel) or ctx.author.id in ctx.bot.DEVS:
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

    __slots__ = ('bot', 'database', '__local_check')

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

    __slots__ = ('start', 'end', 'members')

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

    def begin(self, tz):
        """Starts the PW, assumes it isn't started"""
        self.start = dt.datetime.now(tz=tz)
        for member in self.members:
            if not member.get_started():
                member.begin(self.start)

    def finish(self, tz):
        """Ends the PW, assumes it isn't ended"""
        self.end = dt.datetime.now(tz=tz)
        for member in self.members:
            if not member.get_finished():
                member.finish(self.end)

    def join(self, member, tz):
        """Have a new member join the PW."""
        if PWMember(member) not in self.members and self.get_finished() is not True:
            new_mem = PWMember(member)
            if self.get_started():
                new_mem.begin(dt.datetime.now(tz=tz))
            self.members.append(new_mem)
            return True
        else:
            return False

    def leave(self, member, tz):
        """Have a member in the PW leave the PW."""
        if PWMember(member) in self.members:
            for user in self.members:
                if user == PWMember(member):
                    if user.get_finished():
                        return 2
                    elif user.get_started():
                        user.finish(dt.datetime.now(tz=tz))
                    else:
                        self.members.remove(user)
                        break
            # check if anyone isn't finished
            for user in self.members:
                if not user.get_finished():
                    return 0
            # if everyone is finished, end the pw
            self.finish(tz)
            return 0
        else:
            return 1


class PWMember:
    """Represents a single member of a PW"""

    __slots__ = ('user', 'start', 'end')

    def __init__(self, user):
        """Create a PWMember object with given member"""
        self.user = user
        self.start = None
        self.end = None

    def __str__(self):
        """Convert PWMember to a string"""
        return str(self.user)

    def __eq__(self, other):
        """Check equality with another PWMember instance"""
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
