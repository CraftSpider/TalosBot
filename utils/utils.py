"""
    Holds utility class and special subclasses for Talos.

    author: CraftSpider
"""

import os
import logging
import traceback
import string
import random
import pathlib
import math

try:
    import google.cloud.error_reporting as g_errors
    error_client = g_errors.Client()
    del g_errors
except (ImportError, OSError):
    error_client = None

from . import parsers, element as el


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

# Maps powers of 1024 to byte suffixes
byte_suffixes = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]

# Folder to store logs in
log_folder = pathlib.Path(__file__).parent.parent / "logs"
if not log_folder.exists():
    log_folder.mkdir()
elif not log_folder.is_dir():
    log.error("Log folder already exists as non-directory")


# Various helper method utilities


def configure_logger(logger, *, handlers=[], formatter=None, level=None, propagate=None):
    """
        Configure a python logger easily
    :param logger: Logger to configure
    :param handlers: handlers to add to the logger
    :param formatter: formatter to set for all the handlers, if None leave their current formatter alone
    :param level: Level to set the logger to
    :param propagate: Whether to have the logger propagate to higher levels
    """

    if level is not None:
        logger.setLevel(level)

    for handler in handlers:
        if handler is None:
            continue
        if formatter is not None:
            handler.setFormatter(formatter)
        logger.addHandler(handler)

    if propagate is not None:
        logger.propagate = propagate


def words_written(time, wpm):
    """
        Takes a length of time in seconds and an average wpm and returns a possible number of words written in that
        timeframe.
    :param time: Time in seconds
    :param wpm: Average words per minute
    :return: Number of words written
    """
    time = time / 60
    return int(wpm * time + random.randint(-2 * time, 2 * time))


def time_to_write(words, wpm):
    """
        Takes a number of words and an average wpm, and returns a possible number of seconds required to write that
        many words.
    :param words: Number of words
    :param wpm: Average words per minute
    :return: Time to write words
    """
    time = words / wpm
    return int(time + random.randint(-2 * time * 30, 2 * time * 30))


def pretty_bytes(bytes):
    """
        Convert a number of bytes to a human-prefix number, EG 14.5 GB. Can handle any number of bytes, up to numbers
        larger than any computer can handle
    :param bytes: Number of bytes total
    :return: The formatted human-readable number of bytes
    """
    power = math.floor(math.log(bytes, 1024))
    suffix = byte_suffixes[power]
    val = bytes / (1024**power)
    return f"{val:.2f} {suffix}"


def key_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """
        Generates random strings for things that need keys. Allows variable size and character lists, if desired.
        NOT CRYPTOGRAPHICALLY SECURE
    :param size: Size of the key to generate
    :param chars: Characters to choose from
    :return: Key composed of given characters with a given size, in random order
    """
    return ''.join(random.choice(chars) for _ in range(size))


def log_error(logger, level, error, message=""):
    """
        Formats and logs an error traceback message
    :param logger: Logger to use
    :param level: Level to log at
    :param error: Error to format into a traceback
    :param message: Message to print before traceback
    """
    if message:
        message += "\n"
    errmsg = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    logger.log(level, message + errmsg)

    if error_client is not None and level >= logging.ERROR:
        error_client.report(errmsg)


def safe_remove(*filenames):
    """
        Remove a series of filenames, ignoring any errors
    :param filenames: Filenames to delete
    """
    for filename in filenames:
        try:
            os.remove(filename)
        except Exception as e:
            log_error(log, logging.DEBUG, e)


def replace_escapes(text):
    """
        Replace escape sequences with the characters they represent
    :param text: string to replace escapes in
    :return: New string with escapes replaced by the represented characters
    """
    escape = False
    out = ""
    for char in text:
        if escape is True:
            if char == "t":
                out += "\t"
            elif char == "n":
                out += "\n"
            elif char == "s":
                out += " "
            else:
                out += char
            escape = False
            continue
        if char == "\\":
            escape = True
        else:
            out += char
    return out


# Case/format checking and manipulation function
#
# Some checker functions form exclusive sets. In an exclusive set, if one function is true, it guarantees that all
# other functions in the set will be false.
#
# Some checker functions imply other functions. If the precondition check returns true, the implied function would
# also return true.
#
# Exclusive sets:
# is_lower_snake, is_upper_snake, is_lower_camel, is_upper_camel, and is_other
# is_snake, is_camel, and is_other
#
# Implications:
# is_lower_snake or is_upper_snake -> is_snake
# is_lower_camel or is_upper_camel -> is_camel


def is_lower_snake(text):
    """
        Check if a string is in a lower_snake_case format
    :param text: String to check
    :return: Whether string is in lower snake format
    """
    if " " in text:
        return False
    return "_" in text and not text.isupper()


def is_upper_snake(text):
    """
        Check if a string is in an UPPER_SNAKE_CASE format
    :param text: String to check
    :return: Whether string is in upper snake format
    """
    if " " in text:
        return False
    return "_" in text and text.isupper()


def is_snake(text):
    """
        Check if a string is in either upper or lower snake case format
    :param text: String to check
    :return: Whether string is in any snake case format
    """
    if " " in text:
        return False
    return "_" in text


def is_lower_camel(text):
    """
        Check if a string is in lowerCamelCase format
    :param text: String to check
    :return: Whether string is in lower camel format
    """
    if " " in text:
        return False
    return text[0].islower() and "_" not in text and not text.islower()


def is_upper_camel(text):
    """
        Check if a string is in UpperCamelCase format
    :param text: String to check
    :return: Whether string is in upper camel format
    """
    if " " in text:
        return False
    return text[0].isupper() and "_" not in text and not text.isupper()


def is_camel(text):
    """
        Check if a string is in either upper or lower camel case format
    :param text: String to check
    :return: Whether string is in any camel case format
    """
    if " " in text:
        return False
    return "_" not in text and not text.isupper() and not text.islower()


def is_other(text):
    """
        Check if string is in neither any camel or snake casing format.
    :param text:
    :return:
    """
    return " " in text or ("_" not in text and text.islower())


def get_type(text):
    """
        Check whether a string matches a given casing structure. Returns a string naming the case, or 'other'
    :param text:
    :return:
    """
    if is_snake(text):
        return ("upper" if is_upper_snake(text) else "lower") + " snake"
    elif is_camel(text):
        return ("upper" if is_upper_camel(text) else "lower") + " camel"
    elif is_other(text):
        return "other"
    return "unknown"


def split_snake(text, fix=True):
    """
        Split a string in snake case format into a tuple of its component words
        By default the result is guaranteed to be all lowercase
    :param text: Text to split
    :param fix: Whether to lowercase the result, or leave capitalization as-is
    :return: Tuple of strings
    """
    out = text.split("_")
    if fix:
        out = map(str.lower, out)
    return tuple(out)


def split_camel(text, fix=True):
    """
        Split a string in camel case format into a tuple of its component words
        By default the result is guaranteed to be all lowercase
    :param text: Text to split
    :param fix: Whether to lowercase the result, or leave capitalization as-is
    :return: Tuple of strings
    """
    out = []
    temp = ""
    upper = False
    for char in text:
        if char.isupper() and not upper:
            upper = True
            if temp:
                out.append(temp)
                temp = ""
        elif upper and char.islower():
            upper = False
            last = temp[-1]
            temp = temp[:-1]
            if temp:
                out.append(temp)
            temp = last
        temp += char
    if temp:
        out.append(temp)
    if fix:
        out = map(str.lower, out)
    return tuple(out)


def to_snake_case(text, upper=False):
    """
        Convert a string into snake case
    :param text: string to convert
    :param upper: whether to use upper snake case
    :return: string in snake case form
    """
    if is_snake(text):
        out = text.lower()
    elif is_camel(text):
        out = "_".join(split_camel(text))
    elif is_other(text):
        out = text.lower().replace(" ", "_")
    else:
        raise ValueError("Bad text input, no formatting done")

    if upper:
        out = out.upper()
    return out.strip("_")


def to_camel_case(text, upper=True):
    """
        Convert a string to camel case
    :param text: string to convert
    :param upper: whether to use upper camel case
    :return: string in camel case form
    """
    if is_snake(text):
        out = "".join(map(str.capitalize, split_snake(text)))
    elif is_camel(text):
        out = text.capitalize()
    elif is_other(text):
        out = text.title().replace(" ", "")
    else:
        raise ValueError("Bad text input, no formatting done")

    if not upper:
        out = out[0].lower() + out[1:]
    return out


def add_spaces(text):
    """
        Convert a camelCase or snake_case string to a space separated string, like `camel Case` or `snake case`.
        Capitalization is preserved.
    :param text: Text to convert to space form
    :return: Text with spaces inserted
    """
    if is_snake(text):
        out = " ".join(split_snake(text, False))
    elif is_camel(text):
        out = " ".join(split_camel(text, False))
    else:
        out = text
    return out


def zero_pad(text, length):
    """
        Zero pad numbers in a string
    :param text: String to pad
    :param length: length to pad numbers to
    :return: padded string
    """
    if length < 0:
        raise ValueError("Cannot pad numbers to a negative size")
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


gen = parsers.TreeGen()


def to_dom(html):
    """
        Convert an HTML string into a new Document object
    :param html: HTML to parse
    :return: new Document object from HTML
    """
    gen.reset()
    gen.feed(html)
    return el.Document(gen.close()[0])


def to_nodes(html):
    """
        Convert an HTML string into a list of head nodes
    :param html: HTML to parse
    :return: list of head nodes in HTML
    """
    gen.reset()
    gen.feed(html)
    return gen.close()
