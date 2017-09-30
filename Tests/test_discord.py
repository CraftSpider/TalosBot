import pytest
import sys
import os
import discord
import discord.ext.commands as dc
sys.path.append(os.getcwd().replace("\\Tests", ""))
sys.path.append(os.getcwd().replace("\\Tests", "") + "/Discord")
print(sys.path)
import Discord.Talos
import Discord.AdminCommands


def test_extension_load():
    bot = Discord.Talos.Talos()
    bot.load_extensions()
    assert len(bot.extensions) == 4, "Didn't load 4 extensions"
    assert "Commands" in bot.extensions, "Didn't load Commands extension"
    assert "UserCommands" in bot.extensions, "Didn't load UserCommands extension"
    assert "AdminCommands" in bot.extensions, "Didn't load AdminCommands extension"
    assert "JokeCommands" in bot.extensions, "Didn't load JokeCommands extension"
    bot.unload_extensions()
    assert len(bot.extensions) == 0, "Didn't unload all extensions"
    assert "Commands" not in bot.extensions, "Didn't unload Commands extension"
    assert "UserCommands" not in bot.extensions, "Didn't unload UserCommands extension"
    assert "AdminCommands" not in bot.extensions, "Didn't unload AdminCommands extension"
    assert "JokeCommands" not in bot.extensions, "Didn't unload JokeCommands extension"


def test_admin_commands():
    bot = Discord.Talos.Talos()
    ACs = Discord.AdminCommands.AdminCommands(bot)
