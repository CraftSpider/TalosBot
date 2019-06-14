
from typing import List, Tuple, Any
import abc
import io


class CLLexer(metaclass=abc.ABCMeta):

    __slots__ = ()

    @abc.abstractmethod
    def lex_lang(self, data: str) -> List[Tuple[str, Any]]: ...

class DefaultCLLexer(CLLexer):

    __slots__ = ("_buffer",)

    _buffer: io.StringIO

    def __init__(self) -> None: ...

    def _recurse(self, text) -> List[Tuple[Any]]: ...

    def _lex_if(self) -> Tuple[str, str, str]: ...

    def _lex_exec(self) -> str: ...

    def lex_lang(self, data: str) -> List[Tuple[Any]]: ...
