"""
    Holds utility class and special subclasses for Talos.

    author: CraftSpider
"""
import os
import logging

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


# Various helper method utilities


def replace_escapes(text):
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


def safe_remove(*filenames):
    """
        Remove a series of filenames, ignoring any errors
    :param filenames: Filenames to delete
    """
    for filename in filenames:
        try:
            os.remove(filename)
        except Exception:
            pass


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


def to_camel_case(text, upper=True):
    """
        Convert a string to camel case
    :param text: string to convert
    :param upper: whether to use upper camel case
    :return: string in camel case form
    """
    out = ""
    for char in text:
        if char == "_" or char == " ":
            upper = True
        else:
            if upper is True:
                char = char.upper()
                upper = False
            out += char
    return out


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


gen = parsers.TreeGen()


def to_dom(html):
    gen.reset()
    gen.feed(html)
    return el.Document(gen.close()[0])


def to_nodes(html):
    gen.reset()
    gen.feed(html)
    return gen.close()
