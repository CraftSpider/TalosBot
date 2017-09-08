import pytest
import importlib

Talos = importlib.import_module("Discord.Talos")


def test_extension_load():
    bot = Talos.Talos()
    bot.load_extensions()
    assert len(bot.extensions) == 3, "Didn't load 3 extensions"
    assert "Commands" in bot.extensions, "Didn't load Commands extension"
    assert "UserCommands" in bot.extensions, "Didn't load UserCommands extension"
    assert "AdminCommands" in bot.extensions, "Didn't load AdminCommands extensions"
