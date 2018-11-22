
import abc

from functools import lru_cache
from . import utils


class Document:
    """
        A page of a website, or in other words an HTML document. Provides insight into the internally stored
        HTML tree
    """

    __slots__ = ("_head",)

    def __init__(self, element):
        """
            Create a document from a given element
        :param element: Head of the HTML tree
        """
        self._head = element

    def _depth_iterator(self, start=None):
        """
            Depth-first iterator through the HTML tree
        :param start: Element to start at, once this and all children have been iterated through iteration will end
        :return: An iterator over the nodes of the document
        """
        cur = start
        if cur is None:
            cur = self._head
        elif cur.first_child is None:
            yield cur
            return
        while True:
            yield cur

            next_node = None
            if cur.first_child is not None:
                next_node = cur.first_child
            else:
                while next_node is None:
                    parent = cur.parent
                    if parent is None:
                        return
                    next_node = parent.next_child(cur)
                    if next_node is None and parent == start:
                        return
                    if next_node is None:
                        cur = parent
            cur = next_node

    def get_by_tag(self, tag, start=None):
        """
            Get all the elements in this document with a given tag
        :param tag: Tag to select on
        :param start: Element to start iteration at, defaults to head
        :return: list of elements with given tag
        """
        out = []
        for node in self._depth_iterator(start):
            if isinstance(node, Element) and node.tag == tag:
                out.append(node)
        return out

    def get_by_id(self, nid):
        """
            Get the element in this document with a given id
        :param nid: ID to get
        :return: Element with ID or None
        """
        for node in self._depth_iterator():
            if isinstance(node, Element) and node.id == nid:
                return node
        return None

    def get_by_name(self, name):
        """
            Get the element in this document with a given name
        :param name: Name to get
        :return: Element with name or None
        """
        for node in self._depth_iterator():
            if isinstance(node, Element) and node.name == name:
                return node
        return None

    def get_by_class(self, classname, start=None):
        """
            Get the elements in this document with a given class
        :param classname: Class to select on
        :param start: Element to start iteration at, defaults to head
        :return: All elements with the given class
        """
        out = []
        for node in self._depth_iterator(start):
            if isinstance(node, Element) and node.has_class(classname):
                out.append(node)
        return out

    def get_first_by_class(self, classname, start=None):
        """
            Get the first element in this document with a given class
        :param classname: Class to select
        :param start: Element to start iteration at, defaults to head
        :return: First element with the given class or None
        """
        for node in self._depth_iterator(start):
            if isinstance(node, Element) and node.has_class(classname):
                return node
        return None


class Node(abc.ABC):
    """
        Node in the DOM tree. Could be an element, content, or some other HTML construct.
        Handles all the stuff most nodes could be expected to handle, and defines the interface that they follow
    """

    __slots__ = ("parent", "child_nodes", "_pos_map")

    def __init__(self):
        """
            Initialize a node, setting the initial values of internal variables
        """
        self.parent = None
        self.child_nodes = []
        self._pos_map = {}

    @property
    @lru_cache()
    def depth(self):
        """
            Check the depth of the current node recursively
        :return: Depth from the head of the tree
        """
        if self.parent is None:
            return 0
        return self.parent.depth + 1

    @property
    @lru_cache()
    def first_child(self):
        """
            Get the first child of this Node, or None
        :return: first child
        """
        if not self.child_nodes:
            return None
        return self.child_nodes[0]

    @first_child.setter
    def first_child(self, value):
        """
            Set the first child node of this node to be the given value
        :param value: new first_child Node
        """
        old = self.child_nodes[0]
        old.parent = None
        del self._pos_map[old]

        self.child_nodes[0] = value
        self._pos_map[value] = 0

    @property
    def last_child(self):
        """
            Get the last child of this Node, or None
        :return: last child
        """
        if not self.child_nodes:
            return None
        return self.child_nodes[-1]

    @last_child.setter
    def last_child(self, value):
        """
            Set the last child node of this node to be the given value
        :param value: new last_child Node
        """
        pos = len(self.child_nodes) - 1

        old = self.child_nodes[pos]
        old.parent = None
        del self._pos_map[old]

        self.child_nodes[pos] = value
        self._pos_map[value] = pos

    @property
    @abc.abstractmethod
    def innertext(self):
        """
            Get the innertext, basically any visual text, contained in this node
        :return: Innertext of the Node
        """

    @property
    @abc.abstractmethod
    def innerhtml(self):
        """
            Get the innerhtml, the HTML representation of any children of this node
        :return: Innerhtml of the Node
        """

    @property
    @abc.abstractmethod
    def outerhtml(self):
        """
            Get the outerhtml, the HTML representation of this node and its children
        :return: Outerhtml of the Node
        """

    def add_child(self, el, pos=-1):
        """
            Add a new child node to this node, optionally with specified positioning. Ensures parent of new child is
            set correctly
        :param el: New child node
        :param pos: Position to insert at, default to inserting at end
        """
        if pos < 0:
            pos = len(self.child_nodes)
            self._pos_map[el] = pos

        self.child_nodes.insert(pos, el)
        el.parent = self

        if pos != len(self.child_nodes):
            for i in range(pos, len(self.child_nodes)):
                el = self.child_nodes[i]
                self._pos_map[el] = i

    @lru_cache()
    def next_child(self, el):
        """
            Get the child node immediately after the passed child node. Will raise a ValueError if el is not a child of
            this node
        :param el: Node to get the child after
        :return: Child immediately after node
        """
        if el.parent != self:
            raise ValueError("Passed element not a child of self")

        length = len(self.child_nodes)
        if length == 1:
            return None
        pos = self._pos_map.get(el)
        if pos + 1 < length:
            return self.child_nodes[pos + 1]
        return None

    def remove_child(self, el):
        """
            Remove a child node from this node. Raises a ValueError if el is not a child of this node.
        :param el: Child node to remove
        """
        if el.parent == self:
            self.child_nodes.remove(el)
            el.parent = None
        else:
            raise ValueError("Passed element not a child of self")

    def set_parent(self, el):
        """
            Set this node's current parent to el. Any existing parent will be removed
        :param el: New parent node
        """
        if self.parent is not None:
            self.parent.remove_child(self)
        el.add_child(self)

    def remove_parent(self):
        """
            Remove the current parent node. This node will no longer be a child of the old parent.
        """
        if self.parent is not None:
            self.parent.remove_child(self)
            self.parent = None
        else:
            raise ValueError("Element has no parent")


class Content(Node):
    """
        Content node, raw data inside of an element
    """

    __slots__ = ("value",)

    def __init__(self, data):
        """
            Initialize content with node data
        :param data: Raw node data
        """
        super().__init__()
        self.value = data

    def __str__(self):
        """
            Get the internal string of the content
        :return: Content value
        """
        return self.value

    def __repr__(self):
        """
            Get the content as it would print in HTML
        :return: Content repr
        """
        spacing = "  " * self.depth
        lines = self.value.split("\n")
        out = ""
        for line in lines:
            out += spacing + line + "\n"
        return out

    @property
    def innertext(self):
        """
            Get the Content innertext, just the value
        :return: Content value
        """
        return self.value

    @innertext.setter
    def innertext(self, value):
        """
            Set the Content innertext
        :param value: Value to set innertext to
        """
        self.value = value

    @property
    def innerhtml(self):
        """
            Get the Content innerhtml
        :return: Content value
        """
        return self.value

    @innerhtml.setter
    def innerhtml(self, value):
        """
            Set the Content innerhtml
        :param value: Value to set innerhtml to
        """
        self.value = value

    @property
    def outerhtml(self):
        """
            Get the Content outerhtml
        :return: Content value
        """
        return self.value

    @outerhtml.setter
    def outerhtml(self, value):
        """
            Set the Content outerhtml
        :param value: Value to set outerhtml to
        :return:
        """
        self.value = value

    def add_child(self, el, pos=-1):
        """
            As Content cannot have children, raise a TypeError
        :param el: Element to add
        :param pos: Position to add at
        """
        raise TypeError("Content cannot have children")

    def remove_child(self, el):
        """
            As Content cannot have children, raise a TypeError
        :param el: Element to remove
        """
        raise TypeError("Content cannot have children")


class Element(Node):
    """
        Element node, a tag and attributes and such in HTML
    """

    __slots__ = ("tag", "_attrs")

    SELF_CLOSING = ["br", "meta", "link", "img"]

    def __init__(self, tag, attrs):
        """
            Initialize Element with a given tag and attributes
        :param tag: Element tag
        :param attrs: Element attributes
        """
        super().__init__()
        self.tag = tag
        self._attrs = attrs
        self.parent = None

    def __str__(self):
        """
            String form of element, just the start tag
        :return: string of Element
        """
        return self.starttag

    def __repr__(self):
        """
            Full string form of element, proper HTML for use in a document
        :return: repl of Element
        """
        return self.outerhtml

    @property
    def classes(self):
        """
            Get the list of classes in this element
        :return: List of strings
        """
        return self._attrs.get("class", "").split()

    @property
    def id(self):
        """
            Get the ID of the current element, or None
        :return: ID of Element
        """
        return self._attrs.get("id", None)

    @property
    def name(self):
        """
            Get the name of the current element, or None
        :return: Name of Element
        """
        return self._attrs.get("name", None)

    @property
    @lru_cache()
    def starttag(self):
        """
            Get the start tag of this Element. Tag and attributes, self closed if tag is self closing
        :return: Element start tag
        """
        attrs = "".join(f" {x}=\"{self._attrs[x]}\"" for x in self._attrs)
        if self.self_closing():
            return f"<{self.tag}{attrs} />"
        return f"<{self.tag}{attrs}>"

    @property
    @lru_cache()
    def endtag(self):
        """
            Get the end tag of this element. Empty string if tag is self closing
        :return: Element end tag
        """
        if self.self_closing():
            return ""
        return f"</{self.tag}>"

    @property
    @lru_cache()
    def innertext(self):
        """
            Get the Element innertext, combination of all child Content nodes
        :return: Element innertext
        """
        return "\n".join(map(lambda x: x.value, filter(lambda x: isinstance(x, Content), self.child_nodes)))

    @innertext.setter
    def innertext(self, value):
        """
            Set the innertext. Remove existing Content nodes, add new Content with value
        :param value: Value to become new innertext
        """
        to_del = list(filter(lambda x: isinstance(x, Content), self.child_nodes))
        for el in to_del:
            self.remove_child(el)
        self.add_child(Content(value))

    @property
    @lru_cache()
    def innerhtml(self):
        """
            Get the innerhtml of this Element, all the children's HTML
        :return: Element innerhtml
        """
        out = ""
        for child in self.child_nodes:
            out += child.outerhtml + "\n"
        return out

    @innerhtml.setter
    def innerhtml(self, value):
        """
            Set the innerhtml of this Element. Parse value into HTML with TreeParser then set
            the list of child nodes to the resulting list of nodes
        :param value: HTML string to set innerhtml to
        """
        els = utils.to_nodes(value)
        children = list(self.child_nodes)
        for child in children:
            self.remove_child(child)
        for el in els:
            self.add_child(el)

    @property
    @lru_cache()
    def outerhtml(self):
        """
            Get the outerhtml of this Element, this element as it would appear in an HTML document
        :return: Element outerhtml
        """
        spacing = "  "

        if self.self_closing():
            return self.starttag

        out = self.starttag + "\n"
        for child in self.child_nodes:
            for line in child.outerhtml.split("\n"):
                out += spacing + line + "\n"
        out += f"</{self.tag}>"
        return out

    @outerhtml.setter
    def outerhtml(self, value):
        """
            Set the outerhtml of this element. Parse value into HTML with TreeParser then set
            self's stuff to the head result
        :param value: HTML string to set outerhtml to
        """
        els = utils.to_nodes(value)
        new_self = els[0]
        if not isinstance(new_self, Element):
            raise TypeError("Cannot replace outerhtml of element with non-element")
        self.tag = new_self.tag
        self._attrs = new_self._attrs
        self.child_nodes = new_self.child_nodes
        self._pos_map = new_self._pos_map

    def get_attribute(self, attr, default=None):
        """
            Get an attribute from this Element
        :param attr: Attribute to get
        :param default: Default if not found
        :return: Found attribute, or default
        """
        return self._attrs.get(attr, default)

    def has_class(self, classname):
        """
            Check if this Element has a given class
        :param classname: Class to check for
        :return: Whether Element is of class
        """
        return classname in self.classes

    def self_closing(self):
        """
            Whether this tag is self closing, ends with /> and doesn't need an end tag
        :return: Boolean of whether tag is self closing
        """
        self.tag in self.SELF_CLOSING or (self.tag == "script" and self.get_attribute("src"))
