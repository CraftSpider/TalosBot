"""
    The start of an attempt to rewrite Chatzy Talos using a python async framework
    This will go wonderfully

    author: CraftSpider
"""

import asyncio
import aiohttp
from yarl import URL
import re
import time
import multidict
import logging
import Chatzy.utils as utils
import random
import html.parser as hparser

log = logging.getLogger("talos.main")


TOKEN_FILE = "token.txt"
SITE_URL = "http://www.chatzy.com/"
CHATZY_VERSION = 1508500329


def js_time():
    return int(round(time.time() * 1000))


def timestamp():
    return int(time.time())


class ChatzyError(Exception):
    pass


class MessageParser(hparser.HTMLParser):

    def __init__(self):
        super().__init__()
        self.type = ""
        self.author = ""
        self.color = ""
        self.text = ""
        self.in_b = False
        self.code = ""
        self.timestamp = 0

    def handle_starttag(self, tag, attrs):
        # print("Encountered start tag:", tag, attrs)
        if tag == "p":
            self.type = attrs[0][1]
        if tag == "b":
            self.in_b = True
            self.color = utils.Color(re.sub(r"color:#|;", "", attrs[0][1]))

    def handle_endtag(self, tag):
        # print("Encountered end tag:", tag)
        if tag == "b":
            self.in_b = False

    def handle_data(self, data):
        # print("Encountered data:", data)
        if self.in_b:
            self.author = data
        else:
            self.text += data.strip(": ")

    def handle_comment(self, data):
        code, data = data.split(":")
        self.code = code
        if code == "XS":
            self.timestamp = data
        elif code == "XCP":
            self.text = data

    def close(self):
        super().close()
        if self.code == "XS":
            return Message(self.type, self.author, self.color, self.text)
        elif self.code == "XCP":
            return Message(self.code, "server", utils.Color(0), self.text + " was kicked")
        else:
            log.warning("Unknown Server Code: ")
            return Message("server", "server", utils.Color(0), "Unknown Server Message")


class Message:

    __slots__ = ("type", "author", "color", "text")

    def __init__(self, type, author, color, text):
        self.type = type
        self.author = author
        self.color = color
        self.text = text

    def __str__(self):
        if self.type == "a":
            return "<" + self.author + "> " + self.text
        elif self.type == "b":
            return self.author + " " + self.text
        else:
            return self.text


class Room:

    __slots__ = ("id", "session", "ident", "last_received", "offset", "nickname", "color", "key", "new_queue", "server",
                 "password", "ssl")

    def __init__(self, room_id, session, *, ssl=False):
        self.id = room_id
        self.ident = ""
        self.session = session
        self.last_received = timestamp()
        self.offset = 0
        self.color = utils.Color(utils.Color.BLACK)
        self.nickname = ""
        self.key = ""
        self.new_queue = []
        self.server = 0
        self.password = ""
        self.ssl = ssl

    @property
    def base_url(self):
        return f"http{'s' if self.ssl else ''}://us{self.server}.chatzy.com/"

    @property
    def url(self):
        return self.base_url + str(self.id)

    @property
    def host(self):
        return f"us{self.server}.chatzy.com"

    async def join(self, site_ident, nickname, *, color=None, password=None):
        self.color = utils.Color(color)
        self.nickname = nickname
        if password is not None:
            self.password = password

        async with self.session.get(f"http://www.chatzy.com/{self.id}") as response:
            page = await response.text()
            self.server = re.search(r"<INPUT .*? name=\"X2457\" value=\"(\d+)\">", page).group(1)

        prelim_join_room_data = multidict.MultiDict([
            ("jsonp:X7245", "undefined"),
            ("X5141", site_ident),
            ("X5865", self.id),
            ("X2940", self.id),  # room Name
            ("X8385", SITE_URL),  # URL referrer?
            ("X7960", CHATZY_VERSION),
            ("X5481", 1),  # always 1
            ("X3190", "enter"),
            ("X6432", self.nickname),
            ("X8049", str(self.color)),
            ("X6577", self.password),
            ("X5455", 2),  # always 2
            ("X7245", "X6766"),
            ("X2457", self.server),
            ("X7380", ""),
            ("X8385", SITE_URL),
            ("X7469", js_time()),
        ])
        join_room_data = {}
        async with self.session.get(self.base_url, params=prelim_join_room_data) as response:
            page = await response.text()

            if re.search(r"You must enter the password to join the room.", page):
                raise ChatzyError("Room requires password")
            elif re.search(r"The password is not correct. It matches neither the room or the administrator password.", page):
                raise ChatzyError("Room password incorrect")
            elif re.search(r"The password is not correct. Leave blank to log in as a regular visitor.", page):
                raise ChatzyError("Admin password incorrect")

            join_params = re.findall(r"name=\"([^\"]*?)\" value=\"([^\"]*?)\"", page)
            for match in join_params:
                if match[0] == "X1263":
                    self.ident = match[1]
                join_room_data[match[0]] = match[1]
        async with self.session.put(self.url, data=join_room_data) as response:
            page = await response.text()
            # print(page)
            self.offset = re.search(r"X7162=(\d+)", page).group(1)
            self.key = re.search(r"var X7173='(\w+)'", page).group(1)

    async def post_message(self, message):
        message_headers = {
            "Host": self.host,
            "Referer": self.url
        }
        message_data = {
            "X7960": CHATZY_VERSION,
            "X7245": "X2928",
            "X1263": self.ident,
            "X7162": self.offset,
            "X9102": self.last_received,  # NOTE: Returns messages after this stamp
            "X7974": message,
            "X6746": 1
        }
        async with self.session.post(self.base_url, headers=message_headers, data=message_data) as response:
            self.process_new_messages(await response.text())

    async def tick(self):
        message_headers = {
            "Host": self.host,
            "Referer": self.url
        }
        params = f"tick:{CHATZY_VERSION}"
        params += "&L"
        params += f"&{self.id}"
        params += "&0130R0"
        params += "&1"
        params += f"&{self.nickname}"
        params += f"&{random.random()}"
        async with self.session.get(self.base_url + "?" + params, headers=message_headers) as response:
            text = await response.text()
            print(text)

    async def get_messages(self):  # WARNING: Returns your own messages
        message_headers = {
            "Host": self.host,
            "Referer": self.url
        }
        params = f"check:{self.id}"
        params += f"&{self.key}"
        params += f"&{self.last_received}"
        params += f"&{self.offset}"
        params += f"&{random.random()}"
        async with self.session.get(self.base_url + "?" + params, headers=message_headers) as response:
            self.process_new_messages(await response.text())
            return self.new_queue

    def process_new_messages(self, text):
        print(text)
        if re.search("X6460", text):
            return []
        self.last_received = re.search(r"X9102=(\d+)", text).group(1)
        self.offset = re.search(r"X7162=(\d+)", text).group(1)
        text = re.sub(r"X9076: (.*)|X9882: ", "", text).strip()
        messages = text.split("\n")
        for message in messages:
            parser = MessageParser()
            parser.feed(message)
            self.new_queue.append(parser.close())

    async def quit(self):
        await self.post_message("/quit")


class Talos:

    __slots__ = ("session", "default_name", "site_ident", "rooms", "room_idents")

    def __init__(self):
        self.session = None
        self.site_ident = None
        self.default_name = None
        self.rooms = []
        self.room_idents = {}

    async def login(self, email, password):
        login_data = {  # TODO: Figure out which of these can be removed?
            # "X7245": "undefined",  # Unknown purpose
            # "X5141": "",  # Appears to hold the user string
            # "X5865": "",  # always defined
            # "X2940": "sign.htm",  # always defined
            "X7960": CHATZY_VERSION,
            "X5481": 1,
            "X3190": "sign",
            "X6511": email,  # login email
            "X3361": 1,  # We're registered. 2 if we were registering.
            # "X8182": "",  # One time code for lost password
            "X9170": password,  # login password
            # "X3941": "",  # New Password field
            # "X8170": "",  # Confirm new password field
            # "X3145": "http://www.chatzy.com/",  # Not sure what this is for
            # "X7719": 1  # Passed if we want to log out others
            # "X8382": 1  # Passed if we want to stay logged in
            # "X6746": 1  # Unknown purpose
        }
        async with self.session.post(SITE_URL, data=login_data) as response:
            usercookie = response.cookies["ChatzyUser"]
            usercookie["expires"] = ""
            self.session.cookie_jar.update_cookies(response.cookies)
        self.session.cookie_jar.update_cookies({"ChatzyPrefs2": "Talos[Bot]&FF0000"}, URL("http://chatzy.com"))
        async with self.session.get(SITE_URL) as response:
            page = await response.text()
            self.site_ident = re.search(r"var X5141='(.*?)'", page).group(1)
            self.default_name = re.search(r"X4468.X8224='.*?>(.*?)'", page).group(1)

    async def join_room(self, room_id, *, nickname=None, **kwargs):
        if nickname is None:
            nickname = self.default_name

        room = Room(room_id, self.session)
        await room.join(self.site_ident, nickname=nickname, **kwargs)
        self.rooms.append(room)
        return room

    async def run(self, email, password):
        print("Running Talos")

        self.session = aiohttp.ClientSession()

        try:
            await self.login(email, password)
            room = await self.join_room(33213837658252, nickname="Talos[Bot]", color=utils.Color(utils.Color.RED))
            inp = ""
            # await room.tick()
            while inp != "QUIT":
                inp = input("> ")
                if inp != "QUIT":
                    if inp != "":
                        await room.post_message(inp)
                    else:
                        await room.get_messages()
                while len(room.new_queue):
                    message = room.new_queue.pop(0)
                    if message.author != room.nickname or message.color != room.color:
                        print(message)
            await room.quit()
        finally:
            self.session.close()


def string_load(filename):
    """
        Loads a file as an array of strings and returns that
    :param filename: name of file to load
    :return: array of strings, each string one line in the file.
    """
    out = []
    with open(filename, 'a+') as file:
        try:
            file.seek(0)
            out = file.readlines()
        except Exception as ex:
            log.error(ex)
    return out


def load_login():
    """
        Loads the token file and returns the token
    :return: Talos client Token
    """
    file = string_load(TOKEN_FILE)
    return file[0].strip().split(";")


def main():
    talos = Talos()
    token = load_login()
    loop = asyncio.get_event_loop()
    task = loop.create_task(talos.run(token[0], token[1]))
    loop.run_until_complete(task)


def test():
    pass


if __name__ == "__main__":
    main()
