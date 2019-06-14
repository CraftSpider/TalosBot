import utils.element as element
import pytest


def test_init_content():
    value = "TestContent"
    node = element.Content(value)
    assert node.value == value


def test_content_depth():
    value = "TestContent"
    node = element.Content(value)
    assert node.depth == 0


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
    node = element.Element("p", {})
    assert node.tag == "p"
    assert node._attrs == {}


def test_element_depth():
    node1 = element.Element("div", {})
    node2 = element.Element("p", {})
    node1.add_child(node2)
    assert node1.depth == 0
    assert node2.depth == 1


def test_element_innertext():
    node1 = element.Element("p", {})
    assert node1.innertext == ""


def test_element_innerhtml():
    node1 = element.Element("div", {})
    node2 = element.Element("p", {})
    node1.add_child(node2)
    assert node1.innerhtml == "<p>\n</p>"
    assert node2.innerhtml == ""


def test_element_outerhtml():
    node1 = element.Element("div", {})
    node2 = element.Element("p", {})
    node1.add_child(node2)
    assert node1.outerhtml == "<div>\n  <p>\n  </p>\n</div>"
    assert node2.outerhtml == "<p>\n</p>"


def test_element_children():
    node1 = element.Element("div", {})
    node2 = element.Element("p", {})
    node1.add_child(node2)
    assert node2 in node1.child_nodes
    assert node2.parent == node1
