
import pytest
import asyncio
import functools
import discord.ext.commands as commands

from discord.ext.test import (
    message, verify_message, verify_embed, empty_queue, sent_queue, verify_file, get_config, backend
)


pytestmark = pytest.mark.usefixtures("testlos_m")


@pytest.fixture(scope="module", autouse=True)
def setup(testlos_m):
    global admin, admess
    guild = get_config().guilds[0]
    admin = backend.make_member(
            backend.make_user("AdminUser", "0001"),
            guild,
            roles=[backend.make_role("Admin", guild, permissions=8)]
        )

    admess = functools.partial(message, member=admin)


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


async def test_latex():
    await message("^latex \\frac{1}{2}")
    if not sent_queue.empty():
        mes = await sent_queue.get()
        if mes.content != "pdflatex command not found" and mes.content != "ghostscript command not found":
            await sent_queue.put(mes)
            verify_file()
        else:
            return
    else:
        pytest.fail()

    await message("^latex \\badcommand")
    verify_message()


async def test_nanowrimo():
    await message("^nanowrimo")
    verify_message("Valid options are 'novel', 'profile', and 'info'.")
    with pytest.raises(commands.MissingRequiredArgument):
        await message("^nano novel")
    await empty_queue()
    await message("^nano novel craftspider")
    if not sent_queue.empty():
        mes = await sent_queue.get()
        if mes.content != "Sorry, I couldn't find that user" and mes.content != "They didn't give me the login info":
            await sent_queue.put(mes)
            verify_embed()

    with pytest.raises(commands.MissingRequiredArgument):
        await message("^nano profile")
    await empty_queue()
    await message("^nano profile craftspider")
    if not sent_queue.empty():
        mes = await sent_queue.get()
        if mes.content != "Sorry, I couldn't find that user on the NaNo site" and mes.content != "They didn't give me the login info":
            await sent_queue.put(mes)
            verify_embed()

    await message("^nano info")
    verify_embed()


async def test_ping():
    await message("^ping")
    verify_message()


async def test_productivitywar():
    member = get_config().members[0]
    member1 = get_config().members[1]

    await message("^pw")
    verify_message()
    await message("^pw end")
    verify_message("There's currently no PW going on. Would you like to **create** one?")
    await message("^pw join")
    verify_message("No PW to join. Maybe you want to **create** one?")
    await message("^pw leave")
    verify_message("No PW to leave. Maybe you want to **create** one?")

    await message("^pw create")
    verify_message("Creating a new PW.")
    await message("^pw create")
    verify_message("There's already a PW going on. Would you like to **join**?")
    await message("^pw join")
    verify_message("You're already in this PW.")
    await message("^pw leave", member=1)
    verify_message("You aren't in the PW! Would you like to **join**?")
    await message("^pw join", member=1)
    verify_message(f"User {member1.display_name} joined the PW.")
    await message("^pw start")
    verify_message("Starting PW")
    await message("^pw leave", member=1)
    verify_message(f"User {member1.display_name} left the PW.")
    await message("^pw leave", member=1)
    verify_message(f"You've already left this PW! Are you going to **end** it?")
    await message("^pw leave")
    verify_message(f"User {member.display_name} left the PW.")
    verify_message("Ending PW.")
    verify_embed()

    await message("^pw create")
    verify_message()
    await message("^pw end")
    verify_message("Deleting un-started PW.")

    await message("^pw create")
    verify_message()
    await message("^pw start")
    verify_message()
    await message("^pw end")
    verify_message("Ending PW.")
    verify_embed()


async def test_quote(database):
    await message("^quote")
    verify_message("There are no quotes available for this guild")
    await message("^quote TestUser Hello World!")
    verify_message("You don't have permission to add quotes, sorry")
    await admess("^quote TestUser Hello World!")
    verify_message("Quote from TestUser added!")

    await message("^quote")
    verify_embed()
    await message("^quote list")
    verify_embed()

    with pytest.raises(commands.CheckFailure):
        await message("^quote remove 1")
    await empty_queue()
    await admess("^quote remove 1")
    verify_message("Removed quote 1")
    await message("^quote")
    verify_message("There are no quotes available for this guild")



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
