
import discord.ext.commands as commands
import utils.dutils as dutils
import inspect
import importlib
import pkgutil


def get_doc(object):
    try:
        doc = object.__doc__
    except AttributeError:
        doc = None
    if not isinstance(doc, str):
        return None
    return doc


def is_docable(attr):  # TODO: properties should be docable
    if isinstance(attr, inspect.Attribute):
        member = attr.object
    else:
        member = attr
    if isinstance(member, commands.Command) or isinstance(member, dutils.EventLoop):
        return True
    return inspect.iscoroutinefunction(member) or inspect.isfunction(member) or inspect.ismethod(member) or \
        inspect.isasyncgenfunction(member) or inspect.isgeneratorfunction(member) or inspect.isclass(member) or \
        isinstance(member, property)


def get_declared(type, predicate=None):
    if not inspect.isclass(type):
        type = type.__class__
    attrs = inspect.classify_class_attrs(type)
    for item in attrs:
        if item.defining_class != type:
            continue
        elif not predicate or predicate(item):
            yield item


def _get_undoc_type(type):
    out = []

    if get_doc(type) is None:
        out.append((type.__name__, type))

    for attr in get_declared(type, is_docable):
        name = attr.name
        member = attr.object
        if inspect.isclass(member):
            out.extend(get_undoced(member))
        elif isinstance(member, commands.Command) or isinstance(member, dutils.EventLoop):
            if get_doc(member.callback) is None or member.description is "":
                out.append((name, member))
        else:
            if get_doc(member) is None:
                out.append((name, member))
    return out


def _get_undoc_pkg(pkg):
    found = False
    result = []
    for finder, pname, ispkg in pkgutil.walk_packages([f"./{pkg}"], f"{pkg}."):
        found = True
        if ispkg:
            continue
        pkg = importlib.import_module(pname)
        for name, member in inspect.getmembers(pkg, is_docable):
            if inspect.isclass(member):
                result.extend(get_undoced(member))
            elif get_doc(member) is None:
                result.append((name, member))
    if not found:
        raise FileNotFoundError("Unable to find any packages for the specified name")
    return result


def get_undoced(obj):
    if inspect.isclass(obj):
        return _get_undoc_type(obj)
    elif isinstance(obj, str):
        return _get_undoc_pkg(obj)
    else:
        raise TypeError("get_undoced invalid for non-class or package name type")
