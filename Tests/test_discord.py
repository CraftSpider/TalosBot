"""
    Tests Talos for discord. Ensures that basic functions work right, and that methods have documentation.
    (Yes, method docstrings are enforced)

    Author: CraftSpider
"""

import discord.ext.commands as commands
import discord.gateway
import inspect
import re
import sys
import os
import pytest
import logging
import asyncio
import asyncio.queues
import time
import json
import websockets
from datetime import datetime
from datetime import timedelta
sys.path.append(os.getcwd().replace("\\Tests", ""))
sys.path.append(os.getcwd().replace("\\Tests", "") + "/Discord")
import Discord.talos as dtalos
import Discord.utils as utils

log = logging.getLogger("tests.talos")


# class TestWebSocket(discord.gateway.DiscordWebSocket):
#
#     shard_id = None
#     state = 1
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         self.sent = asyncio.queues.Queue(2**5, loop=self.loop)
#
#         async def run():
#             while not self.connection_closed.done():
#                 await asyncio.sleep(5, loop=self.loop)
#
#         self.worker_task = asyncio.ensure_future(run(), loop=self.loop)
#
#     async def send_as_json(self, data):
#         try:
#             await self.send(json.dumps(data, separators=(',', ':'), ensure_ascii=True))
#         except websockets.exceptions.ConnectionClosed as e:
#             if not self._can_handle_close(e.code):
#                 raise discord.errors.ConnectionClosed(e, shard_id=self.shard_id) from e
#
#     async def send(self, data):
#         await self.ensure_open()
#
#         await self.sent.put(data)
#
#     @classmethod
#     async def from_client(cls, client, *, shard_id=None, session=None, sequence=None, resume=False, loop=None):
#
#         ws = cls(loop=loop)
#         ws._max_heartbeat_timeout = client._connection.heartbeat_timeout
#
#         return ws
#
#
# class Testlos(dtalos.Talos):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     async def login(self, token, *, bot=True):
#         log.info('logging in using static token')
#         self._connection.is_bot = bot
#
#     async def _connect(self):
#         self.ws = await TestWebSocket.from_client(self, loop=self.loop)
#         while True:
#             try:
#                 await self.ws.poll_event()
#             except discord.gateway.ResumeWebSocket:
#                 self.ws = TestWebSocket(loop=self.loop)
#             except json.decoder.JSONDecodeError as e:
#                 log.error(e)
#
#     async def add_message(self, message):
#         while self.ws is None:
#             await asyncio.sleep(1)
#         await self.ws.messages.put(message)
#
#     async def get_response(self):
#         while self.ws is None:
#             await asyncio.sleep(1)
#         return await self.ws.sent.get()


# Test Talos and cogs

def test_extension_load():
    testlos = dtalos.Talos()
    testlos.load_extensions()

    assert len(testlos.extensions) == len(testlos.STARTUP_EXTENSIONS), "Didn't load  extensions"
    for extension in testlos.STARTUP_EXTENSIONS:
        assert testlos.EXTENSION_DIRECTORY + "." + extension in testlos.extensions,\
            "Didn't load {} extension".format(extension)

    testlos.unload_extensions(["Commands", "AdminCommands"])

    testlos.unload_extensions()
    assert len(testlos.extensions) == 0, "Didn't unload all extensions"
    for extension in testlos.STARTUP_EXTENSIONS:
        assert testlos.EXTENSION_DIRECTORY + "." + extension not in testlos.extensions,\
            "Didn't unload {} extension".format(extension)


def get_unique_member(base_class):
    class_name = re.findall("'.*\\.(.*)'", str(base_class.__class__))[0]

    def predicate(member):
        if not (inspect.isroutine(member) or inspect.isawaitable(member)):
            return False
        match = re.compile("(?<!\\.){}\\.".format(class_name))
        if isinstance(member, commands.Command) or match.findall(object.__str__(member)):
            return True
        return False

    return predicate


def test_method_docs():
    talos = dtalos.Talos()
    talos.load_extensions()
    for name, member in inspect.getmembers(talos, get_unique_member(talos)):
        assert inspect.getdoc(member) is not None, "Talos method missing docstring"
    for cog in talos.cogs:
        cog = talos.cogs[cog]
        for name, member in inspect.getmembers(cog, get_unique_member(cog)):
            if isinstance(member, commands.Command):
                assert inspect.getdoc(member.callback) is not None, "Cog command {} missing docstring".format(name)
                continue
            assert inspect.getdoc(member) is not None, "Cog method {} missing docstring".format(name)


# def test_commands():
#     loop = asyncio.get_event_loop()
#     testlos = Testlos(loop=loop)
#     task = loop.run_in_executor(None, lambda: testlos.run(""))
#     loop.create_task(test_commands_async(testlos))
#     while not task.done():
#         pass
#
#
# async def test_commands_async(testlos):
#     await testlos.add_message('{"t":null,"s":null,"op": 10,"d":{"heartbeat_interval":41250,"_trace":["gateway-prd-main-v5x4"]}}')
#     print(await testlos.get_response())
#     await testlos.add_message('{"t":null,"s":null,"op":11,"d":null}')
#     await testlos.add_message('{"op": 0, "t": "READY", "s": 1, "d": {"user": {"verified": true, "id": "330061997842628623", "avatar": null, "bot": true, "email": null, "mfa_enabled": true, "username": "Testlos", "discriminator": "2178"}, "user_settings": {}, "relationships": [], "session_id": "40d9e80d259005d648606e0739c340a8", "_trace": ["gateway-prd-main-7cr7", "discord-sessions-prd-1-15"], "v": 6, "guilds": [{"unavailable": true, "id": "338137396820443137"}, {"unavailable": true, "id": "346423616881295360"}, {"unavailable": true, "id": "367647133077340162"}], "presences": [], "private_channels": []}}')
#     print(await testlos.get_response())

# Test utils classes

def test_embed_paginator():
    page = utils.EmbedPaginator()

    assert page.size is 8, "Base size is not 8"
    page.set_footer("")
    assert page.size is 0, "Empty Embed isn't size 0"
    page.close_pages()
    assert len(page.pages) is 1, "Empty embed has more than one page"

    pass  # TODO


def test_empty_cursor():
    cursor = utils.EmptyCursor()

    with pytest.raises(StopIteration):
        cursor.__iter__().__next__()

    assert cursor.callproc(None) is None, "callproc did something"
    assert cursor.close() is None, "close did something"
    assert cursor.execute(None) is None, "execute did something"
    assert cursor.executemany(None, None) is None, "executemany did something"

    assert cursor.fetchone() is None, "fetchone not None"
    assert cursor.fetchmany() == list(), "fetchmany not empty list"
    assert cursor.fetchall() == list(), "fetchall not empty list"

    assert cursor.description == tuple(), "description not empty tuple"
    assert cursor.rowcount == 0, "rowcount not 0"
    assert cursor.lastrowid is None, "lastrowid not None"


def test_pw_member():
    member1 = utils.PWMember("Test#0001")
    member2 = utils.PWMember("Test#0002")
    member3 = utils.PWMember("Test#0002")

    assert str(member1) == "Test#0001", "Failed string conversion"

    assert member1 != member2, "Failed difference"
    assert member2 == member3, "Failed equivalence"

    assert member1.get_started() is False, "Claims started before start"
    assert member1.get_finished() is False, "Claims finished before finish"
    assert member1.get_len() == -1, "Length should be -1 before finish"

    with pytest.raises(ValueError, message="Allowed non-time beginning"):
        member1.begin("Hello World!")
    time = datetime(year=2017, month=12, day=31)
    member1.begin(time)

    assert member1.get_started() is True, "Claims not started after start"
    assert member1.get_finished() is False, "Claims finished before finish"
    assert member1.get_len() == -1, "Length should be -1 before finish"

    with pytest.raises(ValueError, message="Allowed non-time ending"):
        member1.finish(2017.3123)
    time = time.replace(minute=30)
    member1.finish(time)

    assert member1.get_started() is True, "Claims not started after start"
    assert member1.get_finished() is True, "Claims not finished after finish"
    assert member1.get_len() == timedelta(minutes=30), "Length should be 30 minutes after finish"


def test_pw():
    pw = utils.PW()

    assert pw.get_started() is False, "Claims started before start"
    assert pw.get_finished() is False, "Claims finished before finish"

    assert pw.join("Test#0001") is True, "New member not successfully added"
    assert pw.join("Test#0001") is False, "Member already in PW still added"
    assert pw.leave("Test#0001") is 0, "Existing member couldn't leave"
    assert "Test#0001" not in pw.members, "Member leaving before start is not deleted"
    assert pw.leave("Test#0001") is 1, "Member successfully left twice"
    assert pw.leave("Test#0002") is 1, "Member left before joining"

    pw = utils.PW()

    pw.join("Test#0001")
    pw.begin()
    assert pw.get_started() is True, "Isn't started after start"
    assert pw.get_finished() is False, "Finished before finish"
    pw.join("Test#0002")
    for member in pw.members:
        assert member.get_started() is True, "Member not started after start"
    pw.leave("Test#0001")
    pw.leave("Test#0002")
    assert pw.get_started() is True, "Isn't started after start"
    assert pw.get_finished() is True, "Isn't finished after all leave"
    for member in pw.members:
        assert member.get_finished() is True, "Member not finished after finish"
    assert pw.leave("Test#0001") is 2, "Member leaving after join not reporting "
    assert pw.join("Test#0003") is False, "Allowed join after finish"

    pw = utils.PW()

    pw.join("Test#0001")
    pw.begin()
    pw.join("Test#0002")
    for member in pw.members:
        assert member.get_started() is True, "Member not started after start"
    pw.finish()
    assert pw.get_started() is True, "Isn't started after start"
    assert pw.get_finished() is True, "Isn't finished after finish called"
    for member in pw.members:
        assert member.get_finished() is True, "Member not finished after finish"
