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
import Chatzy.utils as utils
import random
from Chatzy.parsers import MessageParser, FormInputParser, ScriptVarsParser
from Chatzy.errors import ChatzyError
import Chatzy.taloslog as logging

mainlog = logging.mainlog
resplog = logging.resplog
keylog = logging.keylog
#logging.setLevel(logging.DEBUG)
#keylog.setLevel(logging.DEBUG)


TOKEN_FILE = "token.txt"
SITE_URL = "http://www.chatzy.com/"
CHATZY_VERSION = 1526731560

KEY_DICT = {}


def js_time():
    return int(round(time.time() * 1000))


def timestamp():
    return int(time.time())


class Room:

    __slots__ = ("id", "session", "ident", "last_received", "offset", "nickname", "color", "key", "_new_queue",
                 "server", "password", "ssl", "join_type", "site_ident")

    def __init__(self, room_id, session, site_ident, *, ssl=False):
        self.id = room_id
        self.site_ident = site_ident
        self.ident = ""
        self.join_type = ""
        self.session = session
        self.last_received = timestamp()
        self.offset = 0
        self.color = utils.Color(utils.Color.BLACK)
        self.nickname = ""
        self.key = ""
        self._new_queue = []
        self.server = 0
        self.password = ""
        self.ssl = ssl

    @property
    def join_url(self):
        return SITE_URL + f"{self.id:012}"

    @property
    def base_url(self):
        return f"http{'s' if self.ssl else ''}://us{self.server}.chatzy.com/"

    @property
    def url(self):
        return self.base_url + str(self.id)

    @property
    def host(self):
        return f"us{self.server}.chatzy.com"

    @property
    def headers(self):
        return {
            "Host": self.host,
            "Referer": self.url
        }

    @property
    def prelim_data(self):
        return multidict.MultiDict([
            ("jsonp:" + KEY_DICT["JOIN_TYPE"], "undefined"),
            (KEY_DICT["SITE_IDENT"], self.site_ident),
            (KEY_DICT["ROOM_ID"], f"{self.id:012}"),
            (KEY_DICT["ROOM_NAME"], f"{self.id:012}"),
            (KEY_DICT["SITE_REFFERER?"], ""),  # URL referrer?
            (KEY_DICT["VERSION"], CHATZY_VERSION),
            (KEY_DICT["UNKNOWN_ONE"], 1),  # always 1. Figure this out
            (KEY_DICT["PAGE_TYPE"], "enter"),
            (KEY_DICT["NICKNAME"], self.nickname),
            (KEY_DICT["COLOR"], str(self.color)),
            # (KEY_DICT["ROOM_JOIN_OFFSET"], join_offset),
            (KEY_DICT["ROOM_PASSWORD"], self.password),
            (KEY_DICT["UNKNOWN_TWO"], 2),  # almost always 2
            (KEY_DICT["JOIN_TYPE"], self.join_type),
            (KEY_DICT["SERVER"], self.server),
            (KEY_DICT["UNKNOWN_THREE"], ""),
            (KEY_DICT["SITE_REFFERER?"], SITE_URL),
            ("X9805", js_time()),
        ])

    async def populate_key_dict(self):
        async with self.session.get(self.join_url) as response:
            keylog.info("Populating From Room Form")
            page = await response.text()
            resplog.debug("Populate Room Form:")
            resplog.debug(page)
            form_parser = FormInputParser()
            script_parser = ScriptVarsParser()
            form_parser.feed(page)
            script_parser.feed(page)
            inputs = form_parser.close()
            vars = script_parser.close()
            keylog.debug("Inputs: " + str(inputs) + "\n\n")
            KEY_DICT["NICKNAME"] = inputs[3]["name"]
            KEY_DICT["COLOR"] = inputs[4]["name"]
            KEY_DICT["ROOM_JOIN_OFFSET"] = inputs[5]["name"]
            KEY_DICT["ROOM_PASSWORD"] = inputs[6]["name"]
            KEY_DICT["UNKNOWN_TWO"] = inputs[7]["name"]
            KEY_DICT["JOIN_TYPE"] = inputs[8]["name"]
            KEY_DICT["SERVER"] = inputs[9]["name"]
            KEY_DICT["UNKNOWN_THREE"] = inputs[10]["name"]
            keylog.debug("Vars: " + str(vars) + "\n\n")
            KEY_DICT["SITE_REFFERER?"] = vars[3][0]
            KEY_DICT["ROOM_KEY"] = vars[6][0]
            KEY_DICT["ROOM_IDENT"] = vars[19][0]
            KEY_DICT["DEFAULT_NAME"] = vars[24][0]

        self.nickname = "TalosPopulate"
        join_data = await self._prelim_join()
        self.nickname = ""

        async with self.session.post(self.url, data=join_data) as response:
            keylog.info("Populating From Room")
            page = await response.text()
            resplog.debug("Populate Room Main:")
            resplog.debug(page)
            script_parser = ScriptVarsParser()
            script_parser.feed(page)
            vars = script_parser.close()
            keylog.debug("Vars: " + str(vars) + "\n\n")
            KEY_DICT["LAST_RECEIVED"] = vars[31][0]
            KEY_DICT["ROOM_OFFSET"] = vars[32][0]

    async def _prelim_join(self):
        async with self.session.get(self.join_url) as response:
            page = await response.text()
            resplog.debug("Join Room Form:")
            resplog.debug(page)
            parser = FormInputParser()
            parser.feed(page)
            inputs = parser.close()
            self.server = next(filter(lambda x: x["name"] == KEY_DICT["SERVER"], inputs))["value"]
            self.join_type = next(filter(lambda x: x["name"] == KEY_DICT["JOIN_TYPE"], inputs))["value"]
        join_room_data = {}
        async with self.session.get(self.base_url, params=self.prelim_data, headers=self.headers) as response:
            page = await response.text()
            resplog.debug("Join Room Prelim:")
            resplog.debug(page)

            if re.search(r"You must enter the password to join the room.", page):
                raise ChatzyError("Room requires password")
            elif re.search(r"The password is not correct. It matches neither the room or the administrator password.",
                           page):
                raise ChatzyError("Room password incorrect")
            elif re.search(r"The password is not correct. Leave blank to log in as a regular visitor.", page):
                raise ChatzyError("Admin password incorrect")

            parser = FormInputParser()
            parser.feed(page)
            inputs = parser.close()
            for input in inputs:
                if input["name"] == KEY_DICT["ROOM_IDENT"]:
                    self.ident = input["value"]
                join_room_data[input["name"]] = input["value"]
        return join_room_data

    async def join(self, nickname, *, color=None, password=None):
        self.color = utils.Color(color)
        self.nickname = nickname
        if password is not None:
            self.password = password

        join_data = await self._prelim_join()

        async with self.session.post(self.url, data=join_data) as response:
            page = await response.text()
            resplog.debug("Join Room Main:")
            resplog.debug(page)
            print(page)
            parser = ScriptVarsParser()
            parser.feed(page)
            vars = parser.close()
            print(next(filter(lambda x: x[0] == KEY_DICT["ROOM_OFFSET"], vars)))
            self.offset = next(filter(lambda x: x[0] == KEY_DICT["ROOM_OFFSET"], vars))
            self.key = next(filter(lambda x: x[0] == KEY_DICT["ROOM_KEY"], vars))

    async def post_message(self, message):
        message_data = {
            KEY_DICT["VERSION"]: CHATZY_VERSION,
            KEY_DICT["JOIN_TYPE"]: "X2800",
            KEY_DICT["ROOM_IDENT"]: self.ident,
            KEY_DICT["ROOM_OFFSET"]: self.offset,
            KEY_DICT["LAST_RECEIVED"]: self.last_received,  # NOTE: Returns messages after this stamp
            "X2269": message,
        }
        async with self.session.post(self.base_url, headers=self.headers, data=message_data) as response:
            resplog.debug("Post Message:")
            resplog.debug(await response.text())
            self.process_new_messages(await response.text())

    async def tick(self):
        params = f"tick:{CHATZY_VERSION}"
        params += "&L"
        params += f"&{self.id}"
        params += "&0130R0"
        params += "&1"
        params += f"&{self.nickname}"
        params += f"&{random.random()}"
        async with self.session.get(self.base_url + "?" + params, headers=self.headers) as response:
            page = await response.text()
            resplog.debug("Tick:")
            resplog.debug(page)

    async def get_messages(self):  # WARNING: Returns your own messages
        params = f"check:{self.id}"
        params += f"&{self.key}"
        params += f"&{self.last_received}"
        params += f"&{self.offset}"
        params += f"&{random.random()}"
        async with self.session.get(self.base_url + "?" + params, headers=self.headers) as response:
            page = await response.text()
            resplog.debug("Get Messages:")
            resplog.debug(page)
            self.process_new_messages(page)

    def process_new_messages(self, text):
        if re.search("X1716", text):
            return []
        self.last_received = re.search(KEY_DICT["LAST_RECEIVED"] + r"=(\d+)", text).group(1)
        self.offset = re.search(KEY_DICT["ROOM_OFFSET"] + r"=(\d+)", text).group(1)
        text = re.sub(r"X4257: (.*)|X1645: ", "", text).strip()
        messages = text.split("\n")
        for message in messages:
            parser = MessageParser()
            parser.feed(message)
            self._new_queue.append(parser.close())

    def next_new(self):
        if len(self._new_queue):
            return self._new_queue.pop(0)
        else:
            return None

    async def quit(self):
        await self.post_message("/quit")


class Talos:

    __slots__ = ("session", "default_name", "site_ident", "rooms", "room_idents", "__email", "__password")

    def __init__(self):
        self.session = None
        self.site_ident = None
        self.default_name = None
        self.rooms = []
        self.room_idents = {}
        self.__email = ""
        self.__password = ""

    async def populate_key_dict(self):

        # Grab everything possible from the login page
        async with self.session.post(SITE_URL + "sign.htm") as response:
            global CHATZY_VERSION
            keylog.info("Populating From Login Page")
            page = await response.text()
            resplog.debug("Populate Login Form:")
            resplog.debug(page)
            form_parser = FormInputParser()
            script_parser = ScriptVarsParser()
            form_parser.feed(page)
            script_parser.feed(page)
            inputs = form_parser.close()
            vars = script_parser.close()
            keylog.debug("Inputs: " + str(inputs) + "\n\n")
            KEY_DICT["VERSION"] = inputs[0]["name"]
            CHATZY_VERSION = inputs[0]["value"]
            KEY_DICT["UNKNOWN_ONE"] = inputs[1]["name"]
            KEY_DICT["PAGE_TYPE"] = inputs[2]["name"]
            KEY_DICT["EMAIL"] = inputs[3]["name"]
            KEY_DICT["REGISTERING"] = inputs[4]["name"]
            KEY_DICT["LOST_PASSWORD"] = inputs[6]["name"]
            KEY_DICT["PASSWORD"] = inputs[7]["name"]
            KEY_DICT["NEW_PASSWORD_1"] = inputs[8]["name"]
            KEY_DICT["NEW_PASSWORD_2"] = inputs[9]["name"]
            KEY_DICT["LOGIN_UNKNOWN"] = inputs[10]["name"]
            KEY_DICT["LOGOUT_OTHERS"] = inputs[11]["name"]
            KEY_DICT["STAY_LOGGED_IN"] = inputs[12]["name"]
            keylog.debug("Vars: " + str(vars) + "\n\n")
            KEY_DICT["SITE_IDENT"] = vars[0][0]
            KEY_DICT["ROOM_ID"] = vars[1][0]
            KEY_DICT["ROOM_NAME"] = vars[2][0]

        await self._login()

        # create room, use it to keep populating keys
        blog = Room(0, self.session, self.site_ident)
        await blog.populate_key_dict()

        # May want to now join a the blog to grab more values from it. Yay guaranteed address.

        keylog.info("Key Dict:" + str(KEY_DICT))

    async def login(self, email, password):
        self.__email = email
        self.__password = password
        self._login()

    async def _login(self):
        login_data = {  # TODO: Figure out which of these can be removed?
            # KEY_DICT["JOIN_TYPE"]": "undefined",
            KEY_DICT["SITE_IDENT"]: "",
            KEY_DICT["ROOM_ID"]: "",
            KEY_DICT["ROOM_NAME"]: "sign.htm",
            KEY_DICT["VERSION"]: CHATZY_VERSION,
            KEY_DICT["UNKNOWN_ONE"]: 1,  # Not sure what this means
            KEY_DICT["PAGE_TYPE"]: "sign",
            KEY_DICT["EMAIL"]: self.__email,
            KEY_DICT["REGISTERING"]: 1,  # We're registered. 2 if we were registering.
            KEY_DICT["LOST_PASSWORD"]: "",
            KEY_DICT["PASSWORD"]: self.__password,
            KEY_DICT["NEW_PASSWORD_1"]: "",
            KEY_DICT["NEW_PASSWORD_2"]: "",
            KEY_DICT["LOGIN_UNKNOWN"]: "",  # Not sure what this is for
            KEY_DICT["LOGOUT_OTHERS"]: 0,
            KEY_DICT["STAY_LOGGED_IN"]: 0
        }
        async with self.session.post(SITE_URL, data=login_data) as response:
            resplog.debug("Login Response:")
            resplog.debug(await response.text())
            usercookie = response.cookies["ChatzyUser"]
            usercookie["expires"] = ""
            self.session.cookie_jar.update_cookies(response.cookies)
        self.session.cookie_jar.update_cookies({"ChatzyPrefs2": "Talos[Bot]&FF0000"}, URL("http://chatzy.com"))
        async with self.session.get(SITE_URL) as response:
            page = await response.text()
            resplog.debug("Login Main Page:")
            resplog.debug(page)
            parser = ScriptVarsParser()
            parser.feed(page)
            vars = parser.close()
            self.site_ident = vars[0][1].strip("'")
            self.default_name = re.search(r"'<.*?>(.*?)'", vars[8][1]).group(1)

    async def join_room(self, room_id, *, nickname=None, **kwargs):
        if nickname is None:
            nickname = self.default_name

        room = Room(room_id, self.session, self.site_ident)
        await room.join(nickname=nickname, **kwargs)
        self.rooms.append(room)
        return room

    async def run(self, email, password):
        mainlog.info("Running Talos")

        self.session = aiohttp.ClientSession()
        self.__email = email
        self.__password = password

        try:
            await self.populate_key_dict()
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
                message = room.next_new()
                while message:
                    if message.author != room.nickname or message.color != room.color:
                        print(message)
                    message = room.next_new()
            await room.quit()
        finally:
            await self.session.close()


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
            mainlog.error(ex)
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
