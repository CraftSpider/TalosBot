
import asyncio
import logging
import pytest

import discord_talos.talos as talos
import tests.class_factories as dfacts
import tests.dpy_runner as runner
import discord.ext.commands as commands

from tests.dpy_runner import call, verify_message, empty_queue, verify_embed, verify_file, sent_queue

log = logging.getLogger("talos.tests")
testlos: talos.Talos = None
test_values = {}

pytestmark = pytest.mark.usefixtures("testlos_m")


@pytest.fixture(scope="module", autouse=True)
def module_test_values():
    global test_values
    log.debug("Setting up test values")

    runner.configure(testlos, 1, 1, 1)

    channels = 1
    members = 1

    test_values = dict()
    test_values["guild"] = dfacts.make_guild("Test_Guild", owner=True)
    i = 0
    for i in range(channels):
        test_values["channel_{}".format(i + 1)] = dfacts.make_text_channel("Channel_{}".format(i), test_values["guild"])
    for i in range(members):
        test_values["member_{}".format(i + 1)] = dfacts.make_member("Test", "{:04}".format(i+1), test_values["guild"])

    test_values["me"] = dfacts.make_member("Testlos", f"{i+1:04}", test_values["guild"],
                                           id_num=dfacts.get_state().user.id)
    test_values["dev"] = dfacts.make_member("Dev", f"{i+1:04}", test_values["guild"], id_num=talos.Talos.DEVS[0])

    yield

    log.debug("Tearing down test values")
    test_values = dict()


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
    await call("^generate prompt")
    verify_message("Valid options are 'prompt', 'crawl', and 'name'.", False)
    await call("^generate crawl")
    verify_message("Valid options are 'prompt', 'crawl', and 'name'.", False)
    await call("^generate name")
    verify_message("Valid options are 'prompt', 'crawl', and 'name'.", False)
    await call("^generate name 0")
    verify_message("Number must be between 1 and 6 inclusive.")
    await call("^generate name 7")
    verify_message("Number must be between 1 and 6 inclusive.")

    await call("^info")
    verify_embed()

    await call("^nanowrimo")
    verify_message("Valid options are 'novel', 'profile', and 'info'.")

    with pytest.raises(commands.MissingRequiredArgument):
        await call("^nano novel")
    await empty_queue()
    await call("^nano novel craftspider")
    if not sent_queue.empty():
        message = await sent_queue.get()
        if message.message != "Sorry, I couldn't find that user":
            await sent_queue.put(message)
            verify_embed()

    with pytest.raises(commands.MissingRequiredArgument):
        await call("^nano profile")
    await empty_queue()
    await call("^nano profile craftspider")
    if not sent_queue.empty():
        message = await sent_queue.get()
        if message.message != "Sorry, I couldn't find that user on the NaNo site":
            await sent_queue.put(message)
            verify_embed()

    await call("^nano info")
    verify_embed()

    # We don't test ping, as that's beyond our current connection spoofing, and a trivial command.

    # TODO: Productivity war calls

    with pytest.raises(commands.MissingRequiredArgument):
        await call("^roll")
    await empty_queue()
    await call("^roll bad_data")
    verify_message("Either specify a single number for max roll or input NdN format")
    await call("^roll 0d1")
    verify_message("Minimum first value is 1")
    await call("^roll 1d0")
    verify_message("Minimum second value is 1")
    await call("^roll 1")
    verify_message("Result: 1")
    await call("^roll 1d1")
    verify_message("Result: 1")
    await call("^roll 2d1")
    verify_message("Total: 2\nIndividual Rolls: 1, 1")

    await call("^time")
    verify_message()

    await call("^tos")
    verify_message()

    await call("^uptime")
    verify_message()

    await call("^version")
    verify_message(f"Version: {testlos.VERSION}")


async def test_ww():
    with pytest.raises(commands.MissingRequiredArgument):
        await call("^ww")
    await empty_queue()
    await call("^ww bad")
    verify_message("Please specify the length of your word war (in minutes).")
    await call("^ww 0")
    verify_message("Please choose a length between 1 and 60 minutes.")
    await call("^ww 1")
    verify_message()
    await asyncio.sleep(61)
    verify_message()


async def test_admin_commands():
    raise pytest.skip("Admin Command testing not yet implemented")  # TODO


async def test_dev_commands():
    raise pytest.skip("Dev Command testing not yet implemented")  # TODO


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

    await call("^smbc")
    verify_embed()


async def test_user_commands():
    raise pytest.skip("User Command testing not yet implemented")  # TODO
