
import functools
import pytest
import discord.ext.commands as commands

from discord.ext.test import backend, get_config
from discord.ext.test import message, verify_message, verify_embed, verify_file


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


async def test_nick():
    await admess("^nick NewNick")
    verify_message("Nickname changed to NewNick")
    assert testlos.guilds[0].me.display_name == "NewNick"
    with pytest.raises(commands.CheckFailure):
        await message("^nick BadNick")
    verify_message()
    assert testlos.guilds[0].me.display_name == "NewNick"


async def test_repeat():
    pytest.skip()


async def test_purge():
    pytest.skip()


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


async def test_command():
    pytest.skip()


async def test_event():
    pytest.skip()
