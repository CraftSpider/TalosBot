
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
    assert len(result) is 0, f"Missing documentation on {', '.join(map(lambda x: x[0], result))}"


def test_stubs():
    raise pytest.skip("Unimplemented")
