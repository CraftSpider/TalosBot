
import pytest
import asyncio
import discord.ext.commands as commands

from discord.ext.test import message, verify_message, verify_embed, empty_queue, sent_queue


pytestmark = pytest.mark.usefixtures("testlos_m")


async def test_choose():
    with pytest.raises(commands.MissingRequiredArgument):
        await message("^choose")
    await empty_queue()  # Clear out error message, that's tested somewhere else
    await message("^choose one_val")
    verify_message("I need at least two choices to choose between!")
    await message("^choose one, two")
    verify_message("I need at least two choices to choose between!", False)


async def test_credits():
    await message("^credits")
    verify_message()


async def test_generate():
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


async def test_info():
    await message("^info")
    verify_embed()


async def test_nanowrimo():
    import spidertools.common.nano as nano
    try:
        await testlos.nano_session.init()
    except nano.InvalidLogin:
        pass

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


async def test_ping():
    await message("^ping")
    verify_message()


async def test_productivitywar():
    pytest.skip("Productivity War testing not yet implemented")


async def test_roll():
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


async def test_time():
    await message("^time")
    verify_message()


async def test_tos():
    await message("^tos")
    verify_message()


async def test_uptime():
    await message("^uptime")
    verify_message()


async def test_version():
    await message("^version")
    verify_message(f"Version: {testlos.VERSION}")


async def test_wordwar():
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
