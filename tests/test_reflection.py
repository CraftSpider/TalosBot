
import inspect
import re
import discord.ext.commands as commands


def get_unique_member(base_class):
    class_name = re.findall("'.*\\.(.*)'", str(base_class.__class__))[0]

    def predicate(member):
        if not (inspect.isroutine(member) or inspect.isawaitable(member)):
            return False
        match = re.compile("(?<!\\.){}\\.".format(class_name))
        if isinstance(member, commands.Command) or match.findall(object.__str__(member)):
            return True
        return False

    return predicate


def test_method_docs(testlos):
    for name, member in inspect.getmembers(testlos, get_unique_member(testlos)):
        assert inspect.getdoc(member) is not None, "Talos method missing docstring"
    for cog in testlos.cogs:
        cog = testlos.cogs[cog]
        for name, member in inspect.getmembers(cog, get_unique_member(cog)):
            if isinstance(member, commands.Command):
                assert inspect.getdoc(member.callback) is not None, "Cog command {} missing docstring".format(name)
                assert member.description is not "", "Cog command {} missing description".format(name)
            else:
                assert inspect.getdoc(member) is not None, "Cog method {} missing docstring".format(name)
