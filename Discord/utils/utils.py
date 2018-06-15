"""
    Holds utility class and special subclasses for Talos.

    author: CraftSpider
"""
import inspect
import itertools
import re
import io
import logging
import aiohttp
import discord
import discord.ext.commands as dcommands
import datetime as dt
from .paginators import PaginatedEmbed


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


class TalosHTTPClient(aiohttp.ClientSession):

    __slots__ = ("username", "password", "btn_key", "cat_key")

    NANO_URL = "https://nanowrimo.org/"
    BTN_URL = "https://www.behindthename.com/"
    CAT_URL = "https://thecatapi.com/api/"
    XKCD_URL = "https://xkcd.com/"

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

    async def get_xkcd(self, xkcd):
        """
            Get the data from an XKCD comic and return it as a dict
        :param xkcd: XKCD to get, or None if current
        :return: Dict of JSON data
        """
        async with self.get(self.XKCD_URL + (f"{xkcd}/" if xkcd else "") + "info.0.json") as response:
            data = await response.text()
            import json
            data = json.loads(data)
        async with self.get(data["img"]) as response:
            data["img_data"] = discord.File(io.BytesIO(await response.read()), data["img"].split("/")[-1])
        return data


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
        options = ctx.bot.database.get_guild_options(ctx.guild.id)
        if not getattr(options, to_snake_case(ctx.command.instance.__class__.__name__)):
            return False
    except KeyError:
        pass
    perms = ctx.bot.database.get_perm_rules(ctx.guild.id, command)
    if len(perms) == 0:
        return True
    perms.sort()
    for perm in perms:
        if perm.perm_type == "user" and perm.target == str(ctx.author):
            return perm.allow
        elif perm.perm_type == "role":
            for role in ctx.author.roles:
                if perm.target == str(role):
                    return perm.allow
        elif perm.perm_type == "channel" and perm.target == str(ctx.channel):
            return perm.allow
        elif perm.perm_type == "guild":
            return perm.allow
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