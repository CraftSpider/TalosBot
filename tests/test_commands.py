
import asyncio
import logging
import pytest
import discord
import discord.ext.commands as commands

import discord_talos.talos as talos
import dpytest
from dpytest import message, verify_message, empty_queue, verify_embed, verify_file, sent_queue, verify_activity

log = logging.getLogger("talos.tests")
testlos: talos.Talos = None

pytestmark = pytest.mark.usefixtures("testlos_m")


#
# Test functions
#


async def test_commands():
    # Ensure database is setup correctly. This function relies on things tested in test_utils
    testlos.database.verify_schema()

    with pytest.raises(commands.MissingRequiredArgument):
        await message("^choose")
    await empty_queue()  # Clear out error message, that's tested somewhere else
    await message("^choose one_val")
    verify_message("I need at least two choices to choose between!")
    await message("^choose one, two")
    verify_message("I need at least two choices to choose between!", False)

    await message("^credits")
    verify_message()

    await message("^generate")
    verify_message("Valid options are 'prompt', 'crawl', and 'name'.")
    await message("^generate prompt")
    verify_message("Valid options are 'prompt', 'crawl', and 'name'.", False)
    await message("^generate crawl")
    verify_message("Valid options are 'prompt', 'crawl', and 'name'.", False)
    await message("^generate name")
    verify_message("Valid options are 'prompt', 'crawl', and 'name'.", False)
    await message("^generate name 0")
    verify_message("Number must be between 1 and 6 inclusive.")
    await message("^generate name 7")
    verify_message("Number must be between 1 and 6 inclusive.")

    await message("^info")
    verify_embed()

    await message("^nanowrimo")
    verify_message("Valid options are 'novel', 'profile', and 'info'.")

    with pytest.raises(commands.MissingRequiredArgument):
        await message("^nano novel")
    await empty_queue()
    await message("^nano novel craftspider")
    if not sent_queue.empty():
        mes = await sent_queue.get()
        if mes.content != "Sorry, I couldn't find that user":
            await sent_queue.put(mes)
            verify_embed()

    with pytest.raises(commands.MissingRequiredArgument):
        await message("^nano profile")
    await empty_queue()
    await message("^nano profile craftspider")
    if not sent_queue.empty():
        mes = await sent_queue.get()
        if mes.content != "Sorry, I couldn't find that user on the NaNo site":
            await sent_queue.put(mes)
            verify_embed()

    await message("^nano info")
    verify_embed()

    await message("^ping")
    verify_message()

    # TODO: Productivity war messages

    with pytest.raises(commands.MissingRequiredArgument):
        await message("^roll")
    await empty_queue()
    await message("^roll bad_data")
    verify_message("Either specify a single number for max roll or input NdN format")
    await message("^roll 0d1")
    verify_message("Minimum first value is 1")
    await message("^roll 1d0")
    verify_message("Minimum second value is 1")
    await message("^roll 1")
    verify_message("Result: 1")
    await message("^roll 1d1")
    verify_message("Result: 1")
    await message("^roll 2d1")
    verify_message("Total: 2\nIndividual Rolls: 1, 1")

    await message("^time")
    verify_message()

    await message("^tos")
    verify_message()

    await message("^uptime")
    verify_message()

    await message("^version")
    verify_message(f"Version: {testlos.VERSION}")


async def test_ww():
    with pytest.raises(commands.MissingRequiredArgument):
        await message("^ww")
    await empty_queue()
    await message("^ww bad")
    verify_message("Please specify the length of your word war (in minutes).")
    await message("^ww 0")
    verify_message("Please choose a length between 1 and 60 minutes.")
    await message("^ww 1")
    verify_message()
    await asyncio.sleep(61)
    verify_message()


async def test_admin_commands():
    raise pytest.skip("Admin Command testing not yet implemented")  # TODO


async def test_dev_commands():
    import functools

    dev = dpytest.backend.make_member(
        dpytest.backend.make_user("DevUser", "0001", id_num=testlos.DEVS[0]),
        dpytest.get_config().guilds[0]
    )

    devmess = functools.partial(message, member=dev)

    # Ensure normal users check failure
    with pytest.raises(commands.CheckFailure):
        await message("^eval print()")
    await empty_queue()

    await devmess("^playing Test Game")
    verify_message()
    verify_activity(discord.Game(name="Test Game"))

    await devmess("^streaming Test Stream")
    verify_message()
    verify_activity(discord.Streaming(name="Test Stream", url="http://www.twitch.tv/talos_bot_"))

    await devmess("^listening Test Sound")
    verify_message()
    verify_activity(discord.Activity(name="Test Sound", type=discord.ActivityType.listening))

    await devmess("^watching Test Video")
    verify_message()
    verify_activity(discord.Activity(name="Test Video", type=discord.ActivityType.watching))

    # TODO: test stop?

    await devmess("^master_nick Newnick")
    verify_message()
    for guild in dpytest.get_config().guilds:
        assert guild.me.nick == "Newnick"

    await devmess("^idlist")
    verify_message()

    await devmess("^eval 1 + 1")
    verify_message("```py\n2\n```")


async def test_joke_commands():
    await message("^aesthetic Sphinx of black quartz, judge my vow")
    verify_message("Ｓｐｈｉｎｘ　ｏｆ　ｂｌａｃｋ　ｑｕａｒｔｚ，　ｊｕｄｇｅ　ｍｙ　ｖｏｗ")

    await message("^catpic")
    verify_file()

    await message("^favor")
    verify_message("I'm afraid I can't do that, TestUser.")

    await message("^hi")
    verify_message("Hello there TestUser")

    await message("^xkcd")
    verify_embed()

    await message("^smbc")
    verify_embed()


async def test_user_commands():
    raise pytest.skip("User Command testing not yet implemented")  # TODO
