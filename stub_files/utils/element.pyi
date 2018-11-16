
from typing import List, Dict, Optional, Any
import abc


class Document:

    __slots__ = ("_head",)

    _head: Node

    def __init__(self, element): ...

    def _depth_iterator(self, start: Element = ...) -> iter(Node): ...

    def get_by_tag(self, tag: str, start: Optional[Element] = ...) -> List[Element]: ...

    def get_by_id(self, nid: str) -> Optional[Element]: ...

    def get_by_name(self, name: str) -> Optional[Element]: ...

    def get_by_class(self, classname: str, start: Element = ...) -> List[Element]: ...

class Node:

    __slots__ = ("parent", "child_nodes", "_pos_map")

    parent: Node
    child_nodes: List[Node]
    _pos_map: Dict[Node, int]

    def __init__(self) -> None: ...

    @property
    def depth(self) -> int: return

    @property
    def first_child(self) -> Optional[Node]: return

    @first_child.setter
    def first_child(self, value: Node) -> None: ...

    @property
    def last_child(self) -> Optional[Node]: return

    @last_child.setter
    def last_child(self, value) -> None: ...

    @property
    @abc.abstractmethod
    def innertext(self) -> str: ...

    @innertext.setter
    @abc.abstractmethod
    def innertext(self, value) -> None: ...

    @property
    @abc.abstractmethod
    def innerhtml(self) -> str: ...

    @innerhtml.setter
    @abc.abstractmethod
    def innerhtml(self, value) -> None: ...

    @property
    @abc.abstractmethod
    def outerhtml(self) -> str: ...

    @outerhtml.setter
    @abc.abstractmethod
    def outerhtml(self, value) -> None: ...

    def add_child(self, el: Node, pos: int = ...): ...

    def next_child(self, el: Node) -> Optional[Node]: ...

    def remove_child(self, el: Node) -> None: ...

    def set_parent(self, el: Node) -> None: ...

    def remove_parent(self) -> None: ...

class Content(Node):

    __slots__ = ("value",)

    value: str

    def __init__(self, data: str) -> None: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    @property
    def innertext(self) -> str: ...

    @innertext.setter
    def innertext(self, value) -> None: ...

    @property
    def innerhtml(self) -> str: ...

    @innerhtml.setter
    def innerhtml(self, value) -> None: ...

    @property
    def outerhtml(self) -> str: ...

    @outerhtml.setter
    def outerhtml(self, value) -> None: ...

class Element(Node):

     __slots__ = ("tag", "_attrs")

     tag: str
     _attrs: Dict[str, str]
     SELF_CLOSING: List[str]

     def __init__(self, tag: str, attrs: Dict[str, str]) -> None: ...

     def __str__(self) -> str: ...

     def __repr__(self) -> str: ...

     @property
     def classes(self) -> List[str]: ...

     @property
     def id(self) -> Optional[str]: ...

     @property
     def name(self) -> Optional[str]: ...

     @property
     def starttag(self) -> str: ...

     @property
     def endtag(self) -> str: ...

     @property
     def innertext(self) -> str: ...

     @innertext.setter
     def innertext(self, value) -> None: ...

     @property
     def innerhtml(self) -> str: ...

     @innerhtml.setter
     def innerhtml(self, value) -> None: ...

     @property
     def outerhtml(self) -> str: ...

     @outerhtml.setter
     def outerhtml(self, value) -> None: ...

     def get_attribute(self, attr: str, default: Any = ...) -> Optional[str]: ...

     def has_class(self, classname: str) -> bool: ...

     def self_closing(self) -> bool: ...