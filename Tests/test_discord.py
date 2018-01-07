"""
    Tests Talos for discord. Ensures that basic functions work right, and that methods have documentation.
    (Yes, method docstrings are enforced)

    Author: CraftSpider
"""

import discord.ext.commands as commands
import inspect
import re
import sys
import os
import pytest
import logging
import asyncio
import asyncio.queues
import datetime as dt
sys.path.append(os.getcwd().replace("\\Tests", ""))
sys.path.append(os.getcwd().replace("\\Tests", "") + "/Discord")
import Tests.class_factories as dfacts
import Discord.talos as dtalos
import Discord.utils as utils

log = logging.getLogger("tests.talos")


# Test Talos and cog plain methods

def test_extension_load():
    testlos = dtalos.Talos()
    testlos.load_extensions()

    assert len(testlos.extensions) == len(testlos.STARTUP_EXTENSIONS), "Didn't load all extensions"
    for extension in testlos.STARTUP_EXTENSIONS:
        assert testlos.EXTENSION_DIRECTORY + "." + extension in testlos.extensions,\
            "Didn't load {} extension".format(extension)

    testlos.unload_extensions(["Commands", "AdminCommands", "DubDub"])

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
    testlos = dtalos.Talos()
    testlos.load_extensions()
    for name, member in inspect.getmembers(testlos, get_unique_member(testlos)):
        assert inspect.getdoc(member) is not None, "Talos method missing docstring"
    for cog in testlos.cogs:
        cog = testlos.cogs[cog]
        for name, member in inspect.getmembers(cog, get_unique_member(cog)):
            if isinstance(member, commands.Command):
                assert inspect.getdoc(member.callback) is not None, "Cog command {} missing docstring".format(name)
                assert member.description is not "", "Cog command {} missing description".format(name)
            else:
                assert inspect.getdoc(member) is not None, "Cog method {} missing docstring".format(name)


# Test Talos commands
test_values = {}
sent_queue = asyncio.queues.Queue()


def test_all_commands():
    loop = asyncio.get_event_loop()
    testlos = dtalos.Talos()
    testlos.load_extensions()
    async_test = loop.create_task(talos_async_tests(testlos))
    loop.run_until_complete(async_test)


async def prepare(channels=1, members=1):
    test_values["guild"] = dfacts.make_guild("Test_Guild")
    for i in range(channels):
        test_values["channel_{}".format(i+1)] = dfacts.make_text_channel("Channel_{}".format(i), test_values["guild"])
    for i in range(members):
        test_values["member_{}".format(i+1)] = dfacts.make_member("Test", "{:04}".format(i), test_values["guild"])


async def call(callback, content, bot, channel=1, member=1):
    if len(test_values) == 0:
        log.error("Attempted to make call before context prepared")
        return
    message = dfacts.make_message(content,
                                  test_values["member_{}".format(member)],
                                  test_values["channel_{}".format(channel)])
    ctx = await dfacts.make_context(callback, message, bot)
    await bot.invoke(ctx)


async def talos_async_tests(testlos):
    await prepare()
    await commands_async(testlos)
    await admin_commands_async(testlos)
    await dev_commands_async(testlos)
    await joke_commands_async(testlos)
    await user_commands_async(testlos)


async def command_callback(*args, **kwargs):
    await sent_queue.put([args, kwargs])


async def commands_async(testlos):
    cog = testlos.cogs["Commands"]  # type: utils.TalosCog
    await call(command_callback, "^uptime", testlos)
    response = await sent_queue.get()
    print(response)


async def admin_commands_async(testlos):
    pass


async def dev_commands_async(testlos):
    pass


async def joke_commands_async(testlos):
    pass


async def user_commands_async(testlos):
    pass


# Test utils classes

def test_embed_paginator():
    page = utils.EmbedPaginator()

    assert page.size is 8, "Base size is not 8"
    page.set_footer("")
    assert page.size is 0, "Empty Embed isn't size 0"
    page.close()
    assert len(page.get_pages()) is 1, "Empty embed has more than one page"

    pass  # TODO finish testing paginator


def test_empty_cursor():
    cursor = utils.EmptyCursor()

    with pytest.raises(StopIteration):
        cursor.__iter__().__next__()

    assert cursor.callproc("") is None, "callproc did something"
    assert cursor.close() is None, "close did something"
    assert cursor.execute("") is None, "execute did something"
    assert cursor.executemany("", []) is None, "executemany did something"

    assert cursor.fetchone() is None, "fetchone not None"
    assert cursor.fetchmany() == list(), "fetchmany not empty list"
    assert cursor.fetchall() == list(), "fetchall not empty list"

    assert cursor.description == tuple(), "description not empty tuple"
    assert cursor.rowcount == 0, "rowcount not 0"
    assert cursor.lastrowid is None, "lastrowid not None"


def test_talos_database():
    database = utils.TalosDatabase(None)

    database.commit()
    assert database.is_connected() is False, "Empty database considered connected"
    assert database.raw_exec("SELECT * FROM ops") == list(), "raw_exec didn't return empty fetchall"

    pass  # TODO test all the database functions


def test_pw_member():
    d_guild = dfacts.make_guild("test")
    pw_member1 = utils.PWMember(dfacts.make_member("Test", "0001", d_guild))
    d_member2 = dfacts.make_member("Test", "0002", d_guild)
    pw_member2 = utils.PWMember(d_member2)
    pw_member3 = utils.PWMember(d_member2)

    assert str(pw_member1) == "Test#0001", "Failed string conversion"

    assert pw_member1 != pw_member2, "Failed difference"
    assert pw_member2 == pw_member3, "Failed equivalence"

    assert pw_member1.get_started() is False, "Claims started before start"
    assert pw_member1.get_finished() is False, "Claims finished before finish"
    assert pw_member1.get_len() == -1, "Length should be -1 before finish"

    with pytest.raises(ValueError, message="Allowed non-time beginning"):
        pw_member1.begin("Hello World!")
    d_time = dt.datetime(year=2017, month=12, day=31)
    pw_member1.begin(d_time)

    assert pw_member1.get_started() is True, "Claims not started after start"
    assert pw_member1.get_finished() is False, "Claims finished before finish"
    assert pw_member1.get_len() == -1, "Length should be -1 before finish"

    with pytest.raises(ValueError, message="Allowed non-time ending"):
        pw_member1.finish(2017.3123)
    d_time = d_time.replace(minute=30)
    pw_member1.finish(d_time)

    assert pw_member1.get_started() is True, "Claims not started after start"
    assert pw_member1.get_finished() is True, "Claims not finished after finish"
    assert pw_member1.get_len() == dt.timedelta(minutes=30), "Length should be 30 minutes after finish"


def test_pw():  # TODO: Add testing for timezones, for now it's just going with UTC always
    pw = utils.PW()

    assert pw.get_started() is False, "Claims started before start"
    assert pw.get_finished() is False, "Claims finished before finish"

    tz = dt.timezone(dt.timedelta(), "UTC")
    d_guild = dfacts.make_guild("test_guild")
    d_member1 = dfacts.make_member("Test", "0001", d_guild)
    d_member2 = dfacts.make_member("Test", "0002", d_guild)
    d_member3 = dfacts.make_member("Test", "0003", d_guild)
    assert pw.join(d_member1, tz) is True, "New member not successfully added"
    assert pw.join(d_member1, tz) is False, "Member already in PW still added"
    assert pw.leave(d_member1, tz) is 0, "Existing member couldn't leave"
    assert d_member1 not in pw.members, "Member leaving before start is not deleted"
    assert pw.leave(d_member1, tz) is 1, "Member successfully left twice"
    assert pw.leave(d_member2, tz) is 1, "Member left before joining"

    pw = utils.PW()

    pw.join(d_member1, tz)
    pw.begin(tz)
    assert pw.get_started() is True, "Isn't started after start"
    assert pw.get_finished() is False, "Finished before finish"
    pw.join(d_member2, tz)
    for member in pw.members:
        assert member.get_started() is True, "Member not started after start"
    pw.leave(d_member1, tz)
    pw.leave(d_member2, tz)
    assert pw.get_started() is True, "Isn't started after start"
    assert pw.get_finished() is True, "Isn't finished after all leave"
    for member in pw.members:
        assert member.get_finished() is True, "Member not finished after finish"
    assert pw.leave(d_member1, tz) is 2, "Member leaving after join not reporting "
    assert pw.join(d_member3, tz) is False, "Allowed join after finish"

    pw = utils.PW()

    pw.join(d_member1, tz)
    pw.begin(tz)
    pw.join(d_member2, tz)
    for member in pw.members:
        assert member.get_started() is True, "Member not started after start"
    pw.finish(tz)
    assert pw.get_started() is True, "Isn't started after start"
    assert pw.get_finished() is True, "Isn't finished after finish called"
    for member in pw.members:
        assert member.get_finished() is True, "Member not finished after finish"
