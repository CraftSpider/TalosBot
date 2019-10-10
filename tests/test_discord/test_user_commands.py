
import pytest

import discord.ext.test as dpytest
from discord.ext.test import message, verify_message, verify_embed, verify_file, get_config


pytestmark = pytest.mark.usefixtures("testlos_m")


async def test_colour():
    config = get_config()
    guild = config.guilds[0]
    member = config.members[0]
    perms = dpytest.backend.make_role("Perms", guild, permissions=0x8)
    await dpytest.add_role(guild.me, perms)

    assert len(member.roles) == 1
    await message("^colour #8F008F")
    assert len(member.roles) == 2
    await message("^colour clear")
    assert len(member.roles) == 1


async def test_register():
    pytest.skip()


async def test_deregister():
    pytest.skip()


async def test_profile():
    pytest.skip()


async def test_user():
    pytest.skip()
