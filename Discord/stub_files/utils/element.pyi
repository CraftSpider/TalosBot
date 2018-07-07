
from typing import List, Dict, Optional, Any


class Document:

    __slots__ = ("_head",)

    _head: Node

    def __init__(self, element): ...

    def _depth_iterator(self, start: Element = ...) -> iter(Node): ...

    def get_by_tag(self, tag: str, start: Optional[Element] = ...) -> List[Element]: ...

    def get_by_id(self, id: str) -> Optional[Element]: ...

    def get_by_name(self, str: str) -> Optional[Element]:

    def get_by_class(self, classname: str, start: Element = ...) -> List[Element]: ...

class Node:

    __slots__ = ("parent", "child_nodes")

    parent: Node
    child_nodes: List[Node]

    def __init__(self) -> None: ...

    @property
    def depth(self) -> int: ...

    @property
    def first_child(self) -> Optional[Node]: ...

    def set_parent(self, el: Node) -> None: ...

    def remove_parent(self) -> None: ...

    def add_child(self, el: Node, pos: int = ...): ...

    def next_child(self, el: Node) -> Optional[Node]: ...

    def remove_child(self, el: Node): ...

class Content(Node):

    __slots__ = ("value",)

    value: str

    def __init__(self, data: str) -> None: ...

    def __str__(self) -> str: ...

class Element(Node):

     __slots__ = ("tag", "_attrs")

     tag: str
     _attrs: Dict[str, str]

     def __init__(self, tag: str, attrs: Dict[str, str]) -> None: ...

     def __str__(self) -> str: ...

     @property
     def classes(self) -> List[str]: ...

     @property
     def id(self) -> Optional[str]: ...

     @property
     def name(self) -> Optional[str]: ...

     @property
     def innertext(self) -> str: ...

     def get_attribute(self, attr: str, default: Any = ...) -> Optional[str]: ...

     def has_class(self, classname: str) -> bool: ...