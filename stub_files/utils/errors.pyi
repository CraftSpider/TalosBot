
from typing import Any


class NanoException(Exception):

    def __init__(self) -> None: ...

    def _set_message(self, *args: Any) -> None: ...

class NotAUser(NanoException):

    username: str

    def __init__(self, username: str) -> None: ...

class NotANovel(NanoException):

    title: str

    def __init__(self, title: str) -> None: ...
