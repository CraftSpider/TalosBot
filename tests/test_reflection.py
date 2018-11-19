
import inspect
import discord.ext.commands as commands
import utils.dutils as dutils
import pkgutil
import importlib


def is_docable(attr):
    member = attr.object
    if isinstance(member, commands.Command) or isinstance(member, dutils.EventLoop):
        return True
    return inspect.iscoroutinefunction(member) or inspect.isfunction(member) or inspect.ismethod(member) or \
        inspect.isasyncgenfunction(member) or inspect.isgeneratorfunction(member) or inspect.isclass(member)


def get_declared(type, predicate=None):
    if not inspect.isclass(type):
        type = type.__class__
    attrs = inspect.classify_class_attrs(type)
    for item in attrs:
        if item.defining_class != type:
            continue
        elif not predicate or predicate(item):
            yield item


def get_undoced(type):
    out = []
    for attr in get_declared(type, is_docable):
        name = attr.name
        member = attr.object
        if isinstance(member, commands.Command) or isinstance(member, dutils.EventLoop):
            if inspect.getdoc(member.callback) is None or member.description is "":
                out.append((name, member))
        else:
            if inspect.getdoc(member) is None:
                out.append((name, member))
    return out


def test_command_docs(testlos):
    result = get_undoced(testlos)
    for attr in get_declared(testlos, is_docable):
        assert inspect.getdoc(attr.object) is not None, "Talos method missing docstring"
    for cog in testlos.cogs:
        cog = testlos.cogs[cog]
        result.extend(get_undoced(cog))
        # for attr in get_declared(cog, is_docable):
        #     name = attr.name
        #     member = attr.object
        #     if isinstance(member, commands.Command):
        #         assert inspect.getdoc(member.callback) is not None, f"Cog command {name} missing docstring"
        #         assert member.description is not "", f"Cog command {name} missing description"
        #     elif isinstance(member, dutils.EventLoop):
        #         assert inspect.getdoc(member.callback) is not None, f"Cog event loop {name} missing docstring"
        #         assert member.description is not "", f"Cog event loop {name} missing description"
        #     else:
        #         assert inspect.getdoc(member) is not None, f"Cog method {name} missing docstring"
    assert len(result) is 0, f"Missing documentation on: {', '.join(map(lambda x: x[0], result))}"


def test_util_docs():

    for finder, name, ispkg in pkgutil.walk_packages(["../utils"], "utils."):
        pkg = importlib.import_module(name)
        print("Module:", name)
        for name, member in inspect.getmembers(pkg, is_docable):
            if name.startswith("__") and name.endswith("__"):
                continue
            if inspect.isclass(member):
                get_undoced(member)
            print(name)
            print(member)
