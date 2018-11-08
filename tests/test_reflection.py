
import inspect
import discord.ext.commands as commands
import utils.dutils as dutils
import pkgutil
import importlib


def isdocable(member):
    if isinstance(member, commands.Command) or isinstance(member, dutils.EventLoop):
        return True
    return inspect.iscoroutinefunction(member) or inspect.isfunction(member) or inspect.ismethod(member) or \
        inspect.isasyncgenfunction(member) or inspect.isgeneratorfunction(member) or inspect.isclass(member)


def isdeclared(member, class_name):
    if isinstance(member, commands.Command) or isinstance(member, dutils.EventLoop):
        member = member.callback
    if not hasattr(member, "__qualname__"):
        return None  # TODO: If possible, resolve whether a variable was declared on this type
    else:
        return member.__qualname__.startswith(class_name + ".") and not inspect.isbuiltin(member)


def get_unique_member(base_class):
    if inspect.isclass(base_class):
        class_name = base_class.__name__
    else:
        class_name = base_class.__class__.__name__

    def predicate(member):
        if isdocable(member) and isdeclared(member, class_name):
            return True
        return False

    return predicate


def getdeclared(type):
    type.mro()
    pass  # TODO: filter getmembers


def test_command_docs(testlos):
    type = testlos.__class__
    for name, member in inspect.getmembers(type, get_unique_member(type)):
        assert inspect.getdoc(member) is not None, "Talos method missing docstring"
    for cog in testlos.cogs:
        cog = testlos.cogs[cog]
        for name, member in inspect.getmembers(cog, get_unique_member(cog)):
            if isinstance(member, commands.Command):
                assert inspect.getdoc(member.callback) is not None, f"Cog command {name} missing docstring"
                assert member.description is not "", f"Cog command {name} missing description"
            elif isinstance(member, dutils.EventLoop):
                assert inspect.getdoc(member.callback) is not None, f"Cog event loop {name} missing docstring"
                assert member.description is not "", f"Cog event loop {name} missing description"
            else:
                assert inspect.getdoc(member) is not None, f"Cog method {name} missing docstring"


def module_filter(member):
    return isdocable(member)


def test_util_docs():

    print()
    for finder, name, ispkg in pkgutil.walk_packages(["../utils"], "utils."):
        pkg = importlib.import_module(name)
        print("Module:", name)
        for name, member in inspect.getmembers(pkg, module_filter):
            if name.startswith("__") and name.endswith("__"):
                continue
            print(name)
            print(member)
