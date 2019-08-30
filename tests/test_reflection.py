
import inspect
import pytest
import spidertools.common.reflection as reflection
from collections import namedtuple


@pytest.mark.parametrize("package", ["discord_talos", "website"])
def test_docs(package):
    result = reflection.get_undoced(package)
    assert len(result) is 0, f"Missing documentation on: {', '.join(map(lambda x: x[0], result))}"


SKIP_DIRS = {"stub_files", "__pycache__", "tests"}


def test_stub_files():
    missing = []

    for code, stub in reflection.walk_with_stub_files(".", skip_dirs=SKIP_DIRS):
        if not stub.exists() or not stub.is_file():
            missing.append(code)

    assert len(missing) == 0, f"Missing stub files for files: {', '.join(map(lambda x: x.name, missing))}"


def _get_type(obj):
    import discord.ext.commands as commands
    if isinstance(obj, commands.Command):
        obj = obj.callback
    obj = inspect.unwrap(obj)

    if inspect.isclass(obj):
        return 'class'
    elif inspect.isroutine(obj):
        return 'async' if inspect.iscoroutinefunction(obj) or inspect.isasyncgenfunction(obj) else 'sync'
    elif isinstance(obj, type(...)):
        return 'ellipsis'
    else:
        return 'unknown'


ItemGenResult = namedtuple("ItemGenResult", "name code stub")


def _clean_name(name, real, stub):
    import discord.ext.commands as commands
    test = real if real is not None else stub
    if isinstance(test, commands.Command):
        test = test.callback
    test = reflection.unwrap(test)
    if isinstance(test, type):
        return test.__name__
    elif inspect.isfunction(test):
        return test.__qualname__
    return name


def _gen_test_id(val):
    import sys
    sys.stdout.write(str(val))
    return val.name.replace(".", "/")


@pytest.mark.parametrize("val",
                         reflection.walk_all_items(".", skip_dirs=SKIP_DIRS, name_cleaner=_clean_name),
                         ids=_gen_test_id)
def test_stub(val):
    name, real, stub = val
    if stub is None:
        pytest.fail(f"Missing stub for object {name}")
    elif real is None:
        pytest.fail(f"Extra stub for object {name}")

    real_type = _get_type(real)
    stub_type = _get_type(stub)

    if real_type != stub_type:
        pytest.fail(f"Type mismatch for objects: {name} - Real: {real_type}, Stub: {stub_type}")
