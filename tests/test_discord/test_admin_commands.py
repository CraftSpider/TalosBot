
import functools
import pytest
import discord.ext.commands as commands

from discord.ext.test import backend, get_config
from discord.ext.test import message, verify_message, empty_queue, verify_file


pytestmark = pytest.mark.usefixtures("testlos_m")
testlos: commands.Bot


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


async def test_normal_user():
    with pytest.raises(commands.CheckFailure):
        await message("^nick Bad")
    await empty_queue()


async def test_nick():
    await admess("^nick NewNick")
    verify_message("Nickname changed to NewNick")
    assert testlos.guilds[0].me.display_name == "NewNick"
    with pytest.raises(commands.CheckFailure):
        await message("^nick BadNick")
    verify_message()
    assert testlos.guilds[0].me.display_name == "NewNick"


async def test_repeat():
    message = "Testing is Fun"
    await admess(f"^repeat {message}")
    verify_message(message)


async def test_purge():
    config = get_config()
    chan = config.channels[0]

    m1 = await message("Before")
    m2 = await message("Fuck")
    m3 = await message("abc")
    m4 = await message("123")

    history = list(map(lambda x: x.id, await chan.history().flatten()))
    assert m1.id in history
    assert m2.id in history
    assert m3.id in history
    assert m4.id in history

    await admess("^purge 4")

    history = list(map(lambda x: x.id, await chan.history().flatten()))
    assert m1.id in history
    assert m2.id not in history
    assert m3.id not in history
    assert m4.id not in history


async def test_kick():
    pytest.skip()


async def test_ban():
    pytest.skip()


async def test_silence():
    pytest.skip()


async def test_admins():
    pytest.skip()


async def test_perms():
    pytest.skip()


async def test_options():
    pytest.skip()


async def test_command(database):
    with pytest.raises(commands.CommandNotFound):
        await message("^testcom")
    await admess("^command add testcom Hello World!")
    verify_message()
    await message("^testcom")
    verify_message("Hello World!")
    with pytest.raises(commands.CommandNotFound):
        await message("^testcom", member=2, channel=2)

    await admess("^command list")
    verify_message()
    await admess("^command edit testcom New Text")
    verify_message()
    await message("^testcom")
    verify_message("New Text")
    await admess("^command remove testcom")
    verify_message()
    with pytest.raises(commands.CommandNotFound):
        await message("^testcom")


async def test_event():
    pytest.skip()
