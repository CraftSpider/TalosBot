
import discord.ext.commands as commands
import utils.dutils as dutils
import inspect


def get_doc(object):
    try:
        doc = object.__doc__
    except AttributeError:
        doc = None
    if not isinstance(doc, str):
        return None
    return doc


def is_docable(attr):
    if isinstance(attr, inspect.Attribute):
        member = attr.object
    else:
        member = attr
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