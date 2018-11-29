
import pathlib
import tests.reflection as reflection
import os


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
SKIP_FILES = ("__init__.py",)


def test_stubs():

    missing = []

    # TODO: change to use filecmp

    for path, dirs, files in os.walk("."):
        root_path = pathlib.Path(path)
        stub_path = pathlib.Path("./stub_files/" + path[2:])

        remove = []
        for item in dirs:
            if item.startswith(".") or item in SKIP_DIRS:
                remove.append(item)
        for item in remove:
            dirs.remove(item)
        files = list(filter(lambda x: x not in SKIP_FILES and x.endswith(".py"), files))

        for file in files:
            code_file = root_path / file
            stub_file = (stub_path / file).with_suffix(".pyi")

            if not stub_file.exists() and not stub_file.is_file():
                missing.append(code_file)

    assert len(missing) == 0, f"Missing stub files for files: {', '.join(map(lambda x: x.name, missing))}"
