

class Document:

    __slots__ = ("_head",)

    def __init__(self, element):
        self._head = element

    def _depth_iterator(self, start=None):
        cur = start
        if cur is None:
            cur = self._head
        while cur is not None:
            yield cur

            next_node = None
            if cur.first_child is not None:
                next_node = cur.first_child
            elif cur == start:
                raise StopIteration
            else:
                while next_node is None:
                    parent = cur.parent
                    if parent is None:
                        raise StopIteration
                    next_node = parent.next_child(cur)
                    if next_node is None and parent == start:
                        raise StopIteration
                    if next_node is None:
                        cur = parent
            cur = next_node

    def get_by_tag(self, tag, start=None):
        out = []
        for node in self._depth_iterator(start):
            if isinstance(node, Element) and node.tag == tag:
                out.append(node)
        return out

    def get_by_id(self, id):
        for node in self._depth_iterator():
            if isinstance(node, Element) and node.id == id:
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


class Node:

    __slots__ = ("parent", "child_nodes")

    def __init__(self):
        self.parent = None
        self.child_nodes = []

    @property
    def depth(self):
        if self.parent is None:
            return 0
        return self.parent.depth + 1

    @property
    def first_child(self):
        if not self.child_nodes:
            return None
        return self.child_nodes[0]

    def set_parent(self, el):
        if self.parent is not None:
            self.parent.remove_child(self)
        self.parent = el

    def remove_parent(self):
        if self.parent is not None:
            self.parent.remove_child(self)
        self.parent = None

    def add_child(self, el, pos=-1):
        if pos < 0:
            pos = len(self.child_nodes)
        self.child_nodes.insert(pos, el)
        el.set_parent(self)

    def next_child(self, el):
        mark = False
        node = None
        for node in self.child_nodes:
            if mark:
                mark = False
                break
            if node == el:
                mark = True
        if mark:
            return None
        return node

    def remove_child(self, el):
        if el.parent == self:
            self.child_nodes.remove(el)
            el.remove_parent()


class Content(Node):

    __slots__ = ("value",)

    def __init__(self, data):
        super().__init__()
        self.value = data

    def __str__(self):
        spacing = " " * self.depth
        return f"{spacing}\"{self.value}\"\n"

    def __repr__(self):
        return f"{self.value}"

    def add_child(self, el, pos=-1):
        raise TypeError("Content cannot have children")

    def remove_child(self, el):
        raise TypeError("Content cannot have children")


class Element(Node):

    __slots__ = ("tag", "_attrs")

    def __init__(self, tag, attrs):
        super().__init__()
        self.tag = tag
        self._attrs = attrs
        self.parent = None

    def __str__(self):
        spacing = " " * self.depth
        attrs = " ".join(f"{x}=\"{self._attrs[x]}\"" for x in self._attrs)
        if attrs:
            attrs = " " + attrs
        out = f"{spacing}<{self.tag}{attrs}>\n"
        for child in self.child_nodes:
            out += str(child)
        out += f"{spacing}</{self.tag}>\n"
        return out

    def __repr__(self):
        attrs = " ".join(f"{x}=\"{self._attrs[x]}\"" for x in self._attrs)
        if attrs:
            attrs = " " + attrs
        return f"<{self.tag}{attrs}>"

    @property
    def classes(self):
        return self._attrs.get("class", "").split()

    @property
    def id(self):
        return self._attrs.get("id", None)

    @property
    def name(self):
        return self._attrs.get("name", None)

    @property
    def innertext(self):
        return "\n".join(map(lambda x: x.value, filter(lambda x: isinstance(x, Content), self.child_nodes)))

    def get_attribute(self, attr, default=None):
        return self._attrs.get(attr, default)

    def has_class(self, classname):
        return classname in self.classes
