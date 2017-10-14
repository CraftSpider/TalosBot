"""
    Tests Talos for discord. Ensures that basic functions work right, and that methods have documentation.
    (Yes, method docstrings are enforced)

    Author: CraftSpider
"""

import discord.ext.commands.core as core
import discord.ext.commands.bot as bot
import inspect
import re
import sys
import os
sys.path.append(os.getcwd().replace("\\Tests", ""))
sys.path.append(os.getcwd().replace("\\Tests", "") + "/Discord")
import Discord.Talos as dtalos


bot_base = bot.Bot("^")


def test_extension_load():
    talos = dtalos.Talos()
    talos.load_extensions()
    assert len(talos.extensions) == 5, "Didn't load 4 extensions"
    assert "Commands" in talos.extensions, "Didn't load Commands extension"
    assert "UserCommands" in talos.extensions, "Didn't load UserCommands extension"
    assert "AdminCommands" in talos.extensions, "Didn't load AdminCommands extension"
    assert "JokeCommands" in talos.extensions, "Didn't load JokeCommands extension"
    assert "EventLoops" in talos.extensions, "Didn't load EventLoops extension"
    talos.unload_extensions()
    assert len(talos.extensions) == 0, "Didn't unload all extensions"
    assert "Commands" not in talos.extensions, "Didn't unload Commands extension"
    assert "UserCommands" not in talos.extensions, "Didn't unload UserCommands extension"
    assert "AdminCommands" not in talos.extensions, "Didn't unload AdminCommands extension"
    assert "JokeCommands" not in talos.extensions, "Didn't unload JokeCommands extension"
    assert "EventLoops" not in talos.extensions, "Didn't unload EventLoops extension"


def get_unique_member(base_class):
    class_name = re.findall("'.*\\.(.*)'", str(base_class.__class__))[0]

    def predicate(member):
        if not (inspect.isroutine(member) or inspect.isawaitable(member)):
            return False
        match = re.compile("(?<!\\.){}\\.".format(class_name))
        if isinstance(member, core.Command) or match.findall(object.__repr__(member)):
            return True
        return False

    return predicate


def test_method_docs():
    talos = dtalos.Talos()
    talos.load_extensions()
    for name, member in inspect.getmembers(talos, get_unique_member(talos)):
        assert inspect.getdoc(member) is not None, "Talos method missing docstring"
    for cog in talos.cogs:
        cog = talos.cogs[cog]
        for name, member in inspect.getmembers(cog, get_unique_member(cog)):
            if isinstance(member, core.Command):
                assert inspect.getdoc(member.callback) is not None, "Cog command {} missing docstring".format(name)
                continue
            assert inspect.getdoc(member) is not None, "Cog method {} missing docstring".format(name)
