
import inspect
import pkgutil
import importlib

import tests.reflection as reflection


def test_command_docs(testlos):
    result = reflection.get_undoced(testlos)
    for cog in testlos.cogs:
        cog = testlos.cogs[cog]
        result.extend(reflection.get_undoced(cog))
    assert len(result) is 0, f"Missing documentation on: {', '.join(map(lambda x: x[0], result))}"


def test_util_docs():
    result = []
    for finder, name, ispkg in pkgutil.walk_packages(["./utils"], "utils."):
        pkg = importlib.import_module(name)
        for name, member in inspect.getmembers(pkg, reflection.is_docable):
            if name.startswith("__") and name.endswith("__"):
                continue
            if inspect.isclass(member):
                result.extend(reflection.get_undoced(member))
            elif reflection.is_docable(member) and reflection.get_doc(member) is None:
                result.append((name, member))
    print(result)
