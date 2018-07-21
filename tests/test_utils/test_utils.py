"""
    Tests Talos for discord. Ensures that basic functions work right, and that methods have documentation.
    (Yes, method docstrings are enforced)

    Author: CraftSpider
"""

import asyncio
import asyncio.queues
import pytest
import logging

import datetime as dt
import class_factories as dfacts
import utils as tutils

log = logging.getLogger("talos.tests")


# Test Talos and cog plain methods

def test_extension_load(testlos):

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

    loop = asyncio.get_event_loop()
    loop.run_until_complete(testlos.close())


# Test utils classes

def test_paginated_helpers():

    assert utils.paginators._suffix(1) is "st"
    assert utils.paginators._suffix(2) is "nd"
    assert utils.paginators._suffix(3) is "rd"
    assert utils.paginators._suffix(4) is "th"

    assert utils.paginators._suffix(11) is "th"
    assert utils.paginators._suffix(21) is "st"

    assert utils.paginators._custom_strftime("{D}", dt.datetime(year=1, month=1, day=1)) == "1st"
    assert utils.paginators._custom_strftime("{D}", dt.datetime(year=1, month=1, day=2)) == "2nd"
    assert utils.paginators._custom_strftime("{D}", dt.datetime(year=1, month=1, day=3)) == "3rd"
    assert utils.paginators._custom_strftime("{D}", dt.datetime(year=1, month=1, day=4)) == "4th"

    assert utils.paginators._custom_strftime("{D}", dt.datetime(year=1, month=1, day=11)) == "11th"
    assert utils.paginators._custom_strftime("{D}", dt.datetime(year=1, month=1, day=21)) == "21st"


def test_paginated_embed():  # TODO: Need to redo due to change to PaginatedEmbed
    page = tutils.PaginatedEmbed()

    # Test empty embed
    assert page.size is 8, "Base size is not 8"
    page.set_footer(text="")
    assert page.size is 0, "Empty Embed isn't size 0"
    page.close()
    assert page.num_pages is 1, "Empty embed has more than one page"
    assert page.num_pages == len(page._built_pages), "Embed num_pages doesn't match number of built pages"

    # # Test simple setters and output
    # colours = [discord.Colour(0xFF00FF)]
    # page = utils.EmbedPaginator(colour=colours)
    #
    # page.set_title("Test Title")
    # page.set_description("Test Description")
    # page.set_author(name="Test#0001", url="http://talosbot.org", avatar="http://test.com")
    # page.set_footer("Test Footer", "http://test.com")
    # page.close()
    # assert page.size == 46, "Embed size incorrect"
    # assert page.pages == 1, "Embed page number incorrect"
    # pages = page.get_pages()
    # assert len(pages) == 1, "Split embed unnecessarily"
    # embed = pages[0]
    # assert embed.title == "Test Title", "Incorrect Title"
    # assert embed.description == "Test Description", "Incorrect Description"
    # assert embed.colour == colours[0], "Embed has wrong colour"
    # assert embed.footer.text == "Test Footer", "Incorrect Footer"
    # assert embed.footer.icon_url == "http://test.com", "Incorrect footer icon"
    # assert embed.author.name == "Test#0001", "Incorrect Author name"
    # assert embed.author.url == "http://talosbot.org", "Incorrect Author url"
    # assert embed.author.icon_url == "http://test.com", "Incorrect Author icon"

    # Test complex setters and output
    pass  # TODO finish testing paginator


def test_empty_cursor():
    cursor = utils.sql.EmptyCursor()

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
    database = tutils.TalosDatabase(None)

    database.commit()
    assert database.is_connected() is False, "Empty database considered connected"
    assert database.raw_exec("SELECT * FROM admins") == list(), "raw_exec didn't return empty fetchall"
    assert database.commit() is False, "Database committed despite not existing?"

    pass  # TODO test all the database functions


def test_data_classes():
    database = tutils.TalosDatabase(None)

    options = utils.data.UserOptions([2, 0, "^"])
    profile = tutils.TalosUser({"profile": utils.data.UserOptions([1, "", 100, ""]),
                                     "invoked": {},
                                     "titles": [],
                                     "options": options})
    database.save_item(options)
    database.save_item(profile)
    # database.remove_item(options)
    # database.remove_item(profile)


def test_pw_member():
    d_guild = dfacts.make_guild("test")
    pw_member1 = tutils.PWMember(dfacts.make_member("Test", "0001", d_guild))
    d_member2 = dfacts.make_member("Test", "0002", d_guild)
    pw_member2 = tutils.PWMember(d_member2)
    pw_member3 = tutils.PWMember(d_member2)

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
    pw = tutils.PW()

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

    pw = tutils.PW()

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

    pw = tutils.PW()

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
