
import pytest

from discord.ext.test import message, verify_message, verify_embed, verify_file


pytestmark = pytest.mark.usefixtures("testlos_m")


async def test_aesthetic():
    await message("^aesthetic Sphinx of black quartz, judge my vow")
    verify_message("Ｓｐｈｉｎｘ　ｏｆ　ｂｌａｃｋ　ｑｕａｒｔｚ，　ｊｕｄｇｅ　ｍｙ　ｖｏｗ")


async def test_catpic():
    await message("^catpic")
    verify_file()


async def test_favor():
    await message("^favor")
    verify_message("I'm afraid I can't do that, TestUser.")


async def test_hi():
    await message("^hi")
    verify_message("Hello there TestUser")


async def test_xkcd():
    await message("^xkcd")
    verify_embed()


async def test_smbc():
    await message("^smbc")
    verify_embed()


async def test_tvtropes():
    await message("^tvtropes ImprovisedGolems")
    verify_message()
