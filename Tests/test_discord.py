import pytest
import sys
import os

print(sys.path)
sys.path.append(os.getcwd().replace("\\Tests", ""))
print(sys.path)
import Discord.Talos

# Talos = importlib.import_module("Discord.Talos", "..")


def test_extension_load():
    bot = Discord.Talos.Talos()
    bot.load_extensions()
    assert len(bot.extensions) == 3, "Didn't load 3 extensions"
    assert "Commands" in bot.extensions, "Didn't load Commands extension"
    assert "UserCommands" in bot.extensions, "Didn't load UserCommands extension"
    assert "AdminCommands" in bot.extensions, "Didn't load AdminCommands extensions"
