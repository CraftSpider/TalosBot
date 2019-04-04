import utils.element as element
import pytest


def test_init_content():
    element.Content("TestContent")


def test_content_innertext():
    value = "TestContent"
    node = element.Content(value)
    assert node.innertext == value


def test_content_innerhtml():
    value = "TestContent"
    node = element.Content(value)
    assert node.innerhtml == value


def test_content_outerhtml():
    value = "TestContent"
    node = element.Content(value)
    assert node.outerhtml == value


def test_content_children():
    node = element.Content("TestContent")
    node2 = element.Content("TestContent2")
    with pytest.raises(TypeError):
        node.add_child(node2)


def test_init_element():
    pytest.skip()


def test_element_innertext():
    pytest.skip()


def test_element_innerhtml():
    pytest.skip()


def test_element_outerhtml():
    pytest.skip()


def test_element_children():
    pytest.skip()


def test_site_parse():
    pytest.skip()
