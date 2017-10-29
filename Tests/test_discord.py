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
import pytest
from datetime import datetime
from datetime import timedelta
sys.path.append(os.getcwd().replace("\\Tests", ""))
sys.path.append(os.getcwd().replace("\\Tests", "") + "/Discord")
import Discord.talos as dtalos
import Discord.utils as utils


bot_base = bot.Bot("^")


def test_extension_load():
    talos = dtalos.Talos()
    talos.load_extensions()

    assert len(talos.extensions) == len(talos.STARTUP_EXTENSIONS), "Didn't load  extensions"
    for extension in talos.STARTUP_EXTENSIONS:
        assert talos.EXTENSION_DIRECTORY + "." + extension in talos.extensions,\
            "Didn't load {} extension".format(extension)

    talos.unload_extensions(["Commands", "AdminCommands"])

    talos.unload_extensions()
    assert len(talos.extensions) == 0, "Didn't unload all extensions"
    for extension in talos.STARTUP_EXTENSIONS:
        assert talos.EXTENSION_DIRECTORY + "." + extension not in talos.extensions,\
            "Didn't unload {} extension".format(extension)


def get_unique_member(base_class):
    class_name = re.findall("'.*\\.(.*)'", str(base_class.__class__))[0]

    def predicate(member):
        if not (inspect.isroutine(member) or inspect.isawaitable(member)):
            return False
        match = re.compile("(?<!\\.){}\\.".format(class_name))
        if isinstance(member, core.Command) or match.findall(object.__str__(member)):
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


def test_embed_paginator():
    page = utils.EmbedPaginator()

    assert page.size is 8, "Base size is not 8"
    page.set_footer("")
    assert page.size is 0, "Empty Embed isn't size 0"
    page.close_pages()
    assert len(page.pages) is 1, "Empty embed has more than one page"

    pass  # TODO


def test_pw_member():
    member1 = utils.PWMember("Test#0001")
    member2 = utils.PWMember("Test#0002")
    member3 = utils.PWMember("Test#0002")

    assert str(member1) == "Test#0001", "Failed string conversion"

    assert member1 != member2, "Failed difference"
    assert member2 == member3, "Failed equivalence"

    assert member1.get_started() is False, "Claims started before start"
    assert member1.get_finished() is False, "Claims finished before finish"
    assert member1.get_len() == -1, "Length should be -1 before finish"

    with pytest.raises(ValueError, message="Allowed non-time beginning"):
        member1.begin("Hello World!")
    time = datetime(year=2017, month=12, day=31)
    member1.begin(time)

    assert member1.get_started() is True, "Claims not started after start"
    assert member1.get_finished() is False, "Claims finished before finish"
    assert member1.get_len() == -1, "Length should be -1 before finish"

    with pytest.raises(ValueError, message="Allowed non-time ending"):
        member1.finish(2017.3123)
    time = time.replace(minute=30)
    member1.finish(time)

    assert member1.get_started() is True, "Claims not started after start"
    assert member1.get_finished() is True, "Claims not finished after finish"
    assert member1.get_len() == timedelta(minutes=30), "Length should be 30 minutes after finish"


def test_pw():
    pw = utils.PW()

    assert pw.get_started() is False, "Claims started before start"
    assert pw.get_finished() is False, "Claims finished before finish"

    assert pw.join("Test#0001") is True, "New member not successfully added"
    assert pw.join("Test#0001") is False, "Member already in PW still added"
    assert pw.leave("Test#0001") is 0, "Existing member couldn't leave"
    assert "Test#0001" not in pw.members, "Member leaving before start is not deleted"
    assert pw.leave("Test#0001") is 1, "Member successfully left twice"
    assert pw.leave("Test#0002") is 1, "Member left before joining"

    pw = utils.PW()

    pw.join("Test#0001")
    pw.begin()
    assert pw.get_started() is True, "Isn't started after start"
    assert pw.get_finished() is False, "Finished before finish"
    pw.join("Test#0002")
    for member in pw.members:
        assert member.get_started() is True, "Member not started after start"
    pw.leave("Test#0001")
    pw.leave("Test#0002")
    assert pw.get_started() is True, "Isn't started after start"
    assert pw.get_finished() is True, "Isn't finished after all leave"
    for member in pw.members:
        assert member.get_finished() is True, "Member not finished after finish"
    assert pw.leave("Test#0001") is 2, "Member leaving after join not reporting "
    assert pw.join("Test#0003") is False, "Allowed join after finish"

    pw = utils.PW()

    pw.join("Test#0001")
    pw.begin()
    pw.join("Test#0002")
    for member in pw.members:
        assert member.get_started() is True, "Member not started after start"
    pw.finish()
    assert pw.get_started() is True, "Isn't started after start"
    assert pw.get_finished() is True, "Isn't finished after finish called"
    for member in pw.members:
        assert member.get_finished() is True, "Member not finished after finish"
