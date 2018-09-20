
import asyncio
import logging
import pytest
import talos

import class_factories as dfacts
import discord.ext.commands as commands

log = logging.getLogger("talos.tests")
testlos: talos.Talos = None
test_values = {}
sent_queue = asyncio.queues.Queue()

pytestmark = pytest.mark.usefixtures("testlos_m")


@pytest.fixture(scope="module", autouse=True)
def module_test_values():
    global test_values
    log.debug("Setting up test values")

    channels = 1
    members = 1

    test_values = dict()
    test_values["guild"] = dfacts.make_guild("Test_Guild", owner=True)
    for i in range(channels):
        test_values["channel_{}".format(i + 1)] = dfacts.make_text_channel("Channel_{}".format(i), test_values["guild"])
    for i in range(members):
        test_values["member_{}".format(i + 1)] = dfacts.make_member("Test", "{:04}".format(i), test_values["guild"])
    test_values["me"] = dfacts.make_member("Testlos", f"{i+1:04}", test_values["guild"],
                                           id_num=dfacts.get_state().user.id)
    test_values["dev"] = dfacts.make_member("Dev", f"{i+1:04}", test_values["guild"], id_num=talos.Talos.DEVS[0])

    yield

    log.debug("Tearing down test values")
    test_values = dict()


#
# Non-test functions
#

def verify_message(text=None, equals=True):
    if text is None:
        equals = not equals
    try:
        response = sent_queue.get_nowait()
        if equals:
            assert response.message == text, "Didn't find expected text"
        else:
            assert response.message != text, "Found unexpected text"
    except asyncio.QueueEmpty:
        raise AssertionError("No message returned by command")


def verify_embed(embed=None, allow_text=False, equals=True):
    if embed is None:
        equals = not equals
    try:
        response = sent_queue.get_nowait()
        if not allow_text:
            assert response.message is None
        elif equals:
            assert response.kwargs["embed"] == embed, "Didn't find expected embed"
        else:
            assert response.kwargs["embed"] != embed, "Found unexpected embed"
    except asyncio.QueueEmpty:
        raise AssertionError("No message returned by command")


def verify_file(file=None, allow_text=False, equals=True):
    if file is None:
        equals = not equals
    try:
        response = sent_queue.get_nowait()
        if not allow_text:
            assert response.message is None
        elif equals:
            assert response.kwargs["file"] == file, "Didn't find expected file"
        else:
            assert response.kwargs["file"] != file, "Found unexpected file"
    except asyncio.QueueEmpty:
        raise AssertionError("No message returned by command")


async def empty_queue():
    while not sent_queue.empty():
        await sent_queue.get()


async def command_callback(content, **kwargs):
    response = dfacts.MessageResponse(content, kwargs)
    await sent_queue.put(response)


async def call(content, bot=None, callback=command_callback, channel=1, member="member_1"):
    if bot is None:
        bot = testlos
    if len(test_values) == 0:
        log.error("Attempted to make call before context prepared")
        return
    message = dfacts.make_message(content,
                                  test_values[member],
                                  test_values[f"channel_{channel}"])
    ctx = await dfacts.make_context(callback, message, bot)
    await bot.invoke(ctx)


#
# Test functions
#


async def test_commands():
    # Ensure database is setup correctly. This function relies on things tested in test_utils
    testlos.database.verify_schema()

    with pytest.raises(commands.MissingRequiredArgument):
        await call("^choose")
    await empty_queue()  # Clear out error message, that's tested somewhere else
    await call("^choose one_val")
    verify_message("I need at least two choices to choose between!")
    await call("^choose one, two")
    verify_message("I need at least two choices to choose between!", False)

    await call("^credits")
    verify_message()

    await call("^generate")
    verify_message("Valid options are 'prompt', 'crawl', and 'name'.")
    await call("^generate crawl")
    verify_message("Valid options are 'prompt', 'crawl', and 'name'.", False)
    await call("^generate name")
    verify_message("Valid options are 'prompt', 'crawl', and 'name'.", False)
    await call("^generate name 0")
    verify_message("Number must be between 1 and 6 inclusive.")
    await call("^generate name 7")
    verify_message("Number must be between 1 and 6 inclusive.")
    await call("^generate prompt")
    verify_message("Valid options are 'prompt', 'crawl', and 'name'.", False)

    await call("^info")
    verify_embed()

    await call("^nanowrimo")
    verify_message("Valid options are 'novel' and 'profile'.")
    with pytest.raises(commands.MissingRequiredArgument):
        await call("^nano novel")
    await empty_queue()
    await call("^nano novel craftspider")
    if not sent_queue.empty():
        message = await sent_queue.get()
        if message.message != "Sorry, I couldn't find that user or novel.":
            await sent_queue.put(message)
            verify_embed()
    with pytest.raises(commands.MissingRequiredArgument):
        await call("^nano profile")
    await empty_queue()
    await call("^nano profile craftspider")
    if not sent_queue.empty():
        message = await sent_queue.get()
        if message.message != "Sorry, I couldn't find that user on the NaNo site.":
            await sent_queue.put(message)
            verify_embed()

    # We don't test ping, as that's beyond our current connection spoofing, and a trivial command.

    # TODO: Productivity war calls

    with pytest.raises(commands.MissingRequiredArgument):
        await call("^roll")
    await empty_queue()
    await call("^roll bad_data")
    verify_message("Format has to be in NdN!")
    await call("^roll 0d1")
    verify_message("Minimum first value is 1")
    await call("^roll 1d0")
    verify_message("Minimum second value is 1")
    await call("^roll 1d1")
    verify_message("1")

    await call("^time")
    verify_message()

    await call("^tos")
    verify_message()

    await call("^uptime")
    verify_message()

    await call("^version")
    verify_message(f"Version: {testlos.VERSION}")

    with pytest.raises(commands.MissingRequiredArgument):
        await call("^ww")
    await empty_queue()
    await call("^ww bad")
    verify_message("Please specify the length of your word war (in minutes).")
    await call("^ww 0")
    verify_message("Please choose a length between 1 and 60 minutes.")
    await call("^ww 1")
    await dfacts.run_all_events()
    verify_message()
    await asyncio.sleep(61)
    verify_message()


async def test_admin_commands():
    pass  # TODO: Admin Command Testing


async def test_dev_commands():
    pass  # TODO: Dev Command Testing


async def test_joke_commands():
    await call("^aesthetic Sphinx of black quartz, judge my vow")
    verify_message("Ｓｐｈｉｎｘ　ｏｆ　ｂｌａｃｋ　ｑｕａｒｔｚ，　ｊｕｄｇｅ　ｍｙ　ｖｏｗ")

    await call("^catpic")
    verify_file()

    await call("^favor")
    verify_message("I'm afraid I can't do that, Test.")

    await call("^hi")
    verify_message("Hello there Test")

    await call("^xkcd")
    verify_embed()


async def test_user_commands():
    pass  # TODO: User Command Testing
