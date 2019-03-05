
import pytest

from discord.ext.test import message, verify_message, verify_embed, verify_file


pytestmark = pytest.mark.usefixtures("testlos_m")


async def test_nick():
    pytest.skip("Nickname testing not yet implemented")
