"""
    Holds utility class and special subclasses for Talos.

    author: CraftSpider
"""
import inspect
import itertools
import logging
import discord
import discord.ext.commands as dcommands
from utils.dutils.paginators import PaginatedEmbed


log = logging.getLogger("talos.utils")

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


# Fundamental Talos classes


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
        return "Type `{0}{1} category` for a list of commands in a category.".format(
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
        self._paginator = PaginatedEmbed()

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

        filtered = await self.filter_command_list()
        if self.is_bot():
            self._paginator.title = "Talos Help"
            self._paginator.description = description+"\n"+await self.get_ending_note()

            for cog in self.command.cogs:
                if cog == "EventLoops" or cog == "DevCommands":
                    continue
                value = inspect.getdoc(self.command.cogs[cog])
                self._paginator.add_field(name=self.capital_split(cog), value=value)
        else:
            filtered = sorted(filtered)
            if filtered:
                value = self._subcommands_field_value(filtered)
                self._paginator.add_field(name='Commands', value=value)

        self._paginator.set_footer(text="Contact CraftSpider in the Talos discord (^info) for further help")
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


def zero_pad(text, length):
    """
        Zero pad numbers in a string
    :param text: String to pad
    :param length: length to pad numbers to
    :return: padded string
    """
    out = ""
    temp = ""
    numeric = False
    for char in text:
        if char.isnumeric():
            numeric = True
            temp += char
        elif numeric:
            numeric = False
            if len(temp) < length:
                temp = "0"*(length-len(temp)) + temp
            out += temp + char
            temp = ""
        else:
            out += char
    if numeric:
        if len(temp) < length:
            temp = "0" * (length - len(temp)) + temp
        out += temp
    return out


def _perms_check(self, ctx):
    """
        Determine whether the command can is allowed to run in this context.
    :param ctx: dcommands.Context object to consider
    :return: whether the command can run
    """
    if isinstance(ctx.channel, discord.abc.PrivateChannel) or ctx.author.id in self.bot.DEVS:
        return True
    command = str(ctx.command)

    try:
        options = self.bot.database.get_guild_options(ctx.guild.id)
        if not getattr(options, to_snake_case(ctx.command.instance.__class__.__name__)):
            return False
    except KeyError:
        pass
    perms = self.bot.database.get_perm_rules(ctx.guild.id, command)
    if len(perms) == 0:
        return True
    perms.sort()
    for perm in perms:
        result = perm.get_allowed(ctx)
        if result is None:
            continue
        return result
    return True


class TalosCog:
    """Super class to all Talos cogs. Sets a default __local_check, and other init stuff."""

    __slots__ = ("bot", "database")

    def __init__(self, bot):
        """Initiates the current cog. Takes an instance of Talos to use while running."""
        self.bot = bot
        self.database = None
        if hasattr(bot, "database"):
            self.database = bot.database
        if not hasattr(self, f"_{self.__class__.__name__}__local_check"):
            self.add_method(_perms_check, f"_{self.__class__.__name__}__local_check")

    def add_method(self, method, name=None):

        def wrapper(*args, **kwargs):
            return method(self, *args, **kwargs)

        setattr(self, name or method.__name__, wrapper)
