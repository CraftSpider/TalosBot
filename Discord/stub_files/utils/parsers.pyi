
from typing import Tuple
from utils.element import Document, Node
import html.parser as parser

class TreeGen(parser.HTMLParser):

    head: Node
    cur: Node

    def __init__(self) -> None: ...

    def close(self) -> Document: ...

    def handle_starttag(self, tag: str, attrs: Tuple[Tuple[str, str]]) -> None: ...

    def handle_endtag(self, tag: str) -> None: ...

    def handle_data(self, data: str) -> None: ...
