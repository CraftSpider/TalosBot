
import functools
import pytest
import discord
import discord.ext.commands as commands

from discord.ext.test import backend, message, verify_message, get_config, empty_queue, verify_activity


pytestmark = pytest.mark.usefixtures("testlos_m")


@pytest.fixture(scope="module", autouse=True)
def setup(testlos_m):
    global dev, devmess
    dev = backend.make_member(
            backend.make_user("DevUser", "0001", id_num=testlos_m.DEVS[0]),
            get_config().guilds[0]
        )

    devmess = functools.partial(message, member=dev)


async def test_normal_user():
    with pytest.raises(commands.CheckFailure):
        await message("^eval print()")
    await empty_queue()


async def test_playing():
    await devmess("^playing Test Game")
    verify_message()
    verify_activity(discord.Game(name="Test Game"))


async def test_streaming():
    await devmess("^streaming Test Stream")
    verify_message()
    verify_activity(discord.Streaming(name="Test Stream", url="http://www.twitch.tv/talos_bot_"))


async def test_listening():
    await devmess("^listening Test Sound")
    verify_message()
    verify_activity(discord.Activity(name="Test Sound", type=discord.ActivityType.listening))


async def test_watching():
    await devmess("^watching Test Video")
    verify_message()
    verify_activity(discord.Activity(name="Test Video", type=discord.ActivityType.watching))


async def test_master_nick():
    await devmess("^master_nick Newnick")
    verify_message()
    for guild in get_config().guilds:
        assert guild.me.nick == "Newnick"


async def test_eval():
    await devmess("^eval 1 + 1")
    verify_message("```py\n2\n```")


async def test_exec():
    await devmess("^exec print(2 * 2)")
    verify_message("```\n4\n```")


async def test_grant_title():
    pytest.skip("Grant title testing not yet implemented")


async def test_revoke_title():
    pytest.skip("Revoke title testing not yet implemented")


async def test_reload():
    pytest.skip("Reload testing not yet implemented")


async def test_sql():
    pytest.skip("SQL testing not yet implemented")


async def test_stop():
    pytest.skip("Stop testing not yet implemented")


async def test_verifysql():
    pytest.skip("VerifySQL testing not yet implemented")
