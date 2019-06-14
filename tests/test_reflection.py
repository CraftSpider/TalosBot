
import pytest
import tests.reflection as reflection


def test_discord_docs():
    result = reflection.get_undoced("discord_talos")
    assert len(result) is 0, f"Missing documentation on: {', '.join(map(lambda x: x[0], result))}"


def test_util_docs():
    result = reflection.get_undoced("utils")
    assert len(result) is 0, f"Missing documentation on: {', '.join(map(lambda x: x[0], result))}"


def test_website_docs():
    result = reflection.get_undoced("website")
    assert len(result) is 0, f"Missing documentation on: {', '.join(map(lambda x: x[0], result))}"


SKIP_DIRS = ("stub_files", "__pycache__", "tests")


def test_stub_files():
    missing = []

    for code, stub in reflection.walk_with_stubs(".", skip_dirs=SKIP_DIRS):
        if not stub.exists() or not stub.is_file():
            missing.append(code)

    assert len(missing) == 0, f"Missing stub files for files: {', '.join(map(lambda x: x.name, missing))}"


def test_stub_classes():
    missing = []

    for code, stub in reflection.walk_with_modules(".", skip_dirs=SKIP_DIRS):
        print(code)
        print(stub)

    pytest.skip()


def test_stub_funcs():
    pytest.skip()
