
from functools import lru_cache
import abc


class Document:

    __slots__ = ("_head",)

    def __init__(self, element):
        self._head = element

    def _depth_iterator(self, start=None):
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
        out = []
        for node in self._depth_iterator(start):
            if isinstance(node, Element) and node.tag == tag:
                out.append(node)
        return out

    def get_by_id(self, nid):
        for node in self._depth_iterator():
            if isinstance(node, Element) and node.id == nid:
                return node
        return None

    def get_by_name(self, name):
        for node in self._depth_iterator():
            if isinstance(node, Element) and node.name == name:
                return node
        return None

    def get_by_class(self, classname, start=None):
        out = []
        for node in self._depth_iterator(start):
            if isinstance(node, Element) and node.has_class(classname):
                out.append(node)
        return out


class Node(abc.ABC):

    __slots__ = ("parent", "child_nodes", "_pos_map")

    def __init__(self):
        self.parent = None
        self.child_nodes = []
        self._pos_map = {}

    @property
    @lru_cache()
    def depth(self):
        if self.parent is None:
            return 0
        return self.parent.depth + 1

    @property
    @lru_cache()
    def first_child(self):
        if not self.child_nodes:
            return None
        return self.child_nodes[0]

    @first_child.setter
    def first_child(self, value):
        old = self.child_nodes[0]
        old.parent = None
        del self._pos_map[old]

        self.child_nodes[0] = value
        self._pos_map[value] = 0

    @property
    @abc.abstractmethod
    def innertext(self): ...

    @property
    @abc.abstractmethod
    def innerhtml(self): ...

    @property
    @abc.abstractmethod
    def outerhtml(self): ...

    def add_child(self, el, pos=-1):
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
        length = len(self.child_nodes)
        if length == 1:
            return None
        pos = self._pos_map.get(el)
        if pos + 1 < length:
            return self.child_nodes[pos + 1]
        return None

    def remove_child(self, el):
        if el.parent == self:
            self.child_nodes.remove(el)
            el.parent = None
        else:
            raise ValueError("Passed element not a child of self")

    def set_parent(self, el):
        if self.parent is not None:
            self.parent.remove_child(self)
        el.add_child(self)

    def remove_parent(self):
        if self.parent is not None:
            self.parent.remove_child(self)
            self.parent = None
        else:
            raise ValueError("Element has no parent")


class Content(Node):

    __slots__ = ("value",)

    def __init__(self, data):
        super().__init__()
        self.value = data

    def __str__(self):
        return f"{self.value}"

    def __repr__(self):
        spacing = "  " * self.depth
        lines = self.value.split("\n")
        out = ""
        for line in lines:
            out += spacing + line + "\n"
        return out

    @property
    def innertext(self):
        return self.value

    @property
    def innerhtml(self):
        return self.value

    @property
    def outerhtml(self):
        return self.value

    def add_child(self, el, pos=-1):
        raise TypeError("Content cannot have children")

    def remove_child(self, el):
        raise TypeError("Content cannot have children")


class Element(Node):

    __slots__ = ("tag", "_attrs")

    SELF_CLOSING = ["br", "meta", "link", "img"]

    def __init__(self, tag, attrs):
        super().__init__()
        self.tag = tag
        self._attrs = attrs
        self.parent = None

    def __str__(self):
        return self.starttag

    def __repr__(self):
        return self.outerhtml

    @property
    @lru_cache()
    def classes(self):
        return self._attrs.get("class", "").split()

    @property
    @lru_cache()
    def id(self):
        return self._attrs.get("id", None)

    @property
    @lru_cache()
    def name(self):
        return self._attrs.get("name", None)

    @property
    @lru_cache()
    def starttag(self):
        attrs = "".join(f" {x}=\"{self._attrs[x]}\"" for x in self._attrs)
        if self.self_closing():
            return f"<{self.tag}{attrs} />"
        return f"<{self.tag}{attrs}>"

    @property
    @lru_cache()
    def endtag(self):
        if self.self_closing():
            return ""
        return f"</{self.tag}>"

    @property
    @lru_cache()
    def innertext(self):
        return "\n".join(map(lambda x: x.value, filter(lambda x: isinstance(x, Content), self.child_nodes)))

    @property
    @lru_cache()
    def innerhtml(self):
        out = ""
        for child in self.child_nodes:
            out += child.outerhtml + "\n"
        return out

    @property
    @lru_cache()
    def outerhtml(self):
        spacing = "  "

        if self.self_closing():
            return self.starttag

        out = self.starttag + "\n"
        for child in self.child_nodes:
            for line in child.outerhtml.split("\n"):
                out += spacing + line + "\n"
        out += f"</{self.tag}>"
        return out

    def get_attribute(self, attr, default=None):
        return self._attrs.get(attr, default)

    def has_class(self, classname):
        return classname in self.classes

    def self_closing(self):
        self.tag in self.SELF_CLOSING or (self.tag == "script" and self.get_attribute("src"))
