
import pytest
import spidertools.discord.errors as derrors

import discord.ext.test as dpytest
from discord.ext.test import message, verify_message, verify_embed, empty_queue, get_config


pytestmark = pytest.mark.usefixtures("testlos_m")


async def test_colour():
    config = get_config()
    guild = config.guilds[0]
    member = config.members[0]
    perms = dpytest.backend.make_role("Perms", guild, permissions=0x8)
    await dpytest.add_role(guild.me, perms)

    assert len(member.roles) == 1

    await message("^colour BadColour")
    verify_message("Unrecognized colour format. Valid formats include `#123456`, `0x123456`, and some names such as "
                   "teal or orange")
    assert len(member.roles) == 1

    await message("^colour #8F008F")
    verify_message(f"{member.display_name}'s colour changed to #8F008F!")
    assert len(member.roles) == 2
    role = guild.roles[1]
    assert member.roles[1] == role

    await message("^colour clear")
    verify_message("Talos colour removed")
    assert len(member.roles) == 1
    assert role not in guild.roles


async def test_register(database):
    await message("^register")
    verify_message("Registered new user!")
    await message("^register")
    verify_message("You're already a registered user.")


async def test_deregister(database):
    await message("^register")
    await empty_queue()
    await message("^deregister")
    verify_message("Deregistered user")

    with pytest.raises(derrors.NotRegistered):
        await message("^deregister")


async def test_profile(database):
    await message("^register")
    await empty_queue()

    member = get_config().members[0]
    member1 = get_config().members[1]

    await message("^profile")
    await verify_embed()
    await message(f"^profile {member.name}")
    await verify_embed()
    with pytest.raises(derrors.NotRegistered):
        await message(f"^profile {member1.name}")


async def test_user(database):
    await message("^register")
    await empty_queue()

    member = get_config().members[0]

    with pytest.raises(derrors.NotRegistered):
        await message("^user", member=1)

    await message("^user")
    verify_message("Valid options are 'options', 'stats', 'title', 'description', 'set', and 'remove'")

    await message("^user titles")
    verify_message("No available titles")

    await message("^user title BadTitle")
    verify_message("You do not have that title")
    await message("^user title")
    verify_message("Title successfully cleared")

    await message("^user options")
    verify_message()

    await message("^user stats")
    verify_message()

    await message("^user description A temporary description")
    verify_message("Description set")

    await message("^user set prefix ^")
    verify_message(f"Option prefix set to `^` for {member.display_name}")
    await message("^user set bad ^")
    verify_message("I don't recognize that option.")

    await message("^user remove prefix")
    verify_message(f"Option prefix set to default for {member.display_name}")
    await message("^user remove bad")
    verify_message("I don't recognize that option.")
