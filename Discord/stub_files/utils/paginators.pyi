
import datetime as dt
from typing import Tuple, List, Dict, overload
import discord
from discord.embeds import Embed, EmbedProxy, EmptyEmbed, _EmptyEmbed

EmptyField = ... # type: EmbedProxy

def _suffix(d: int) -> str: ...

def _custom_strftime(strf: str, t: dt.datetime) -> str: ...

class PaginatedEmbed(Embed):

    __slots__ = ("_built_pages", "_max_size", "repeat_title", "repeat_desc", "repeat_author")

    MAX_TOTAL: int = ...
    MAX_TITLE: int = ...
    MAX_DESCRIPTION: int = ...
    MAX_FIELDS: int = ...
    MAX_FIELD_NAME: int = ...
    MAX_FIELD_VALUE: int = ...
    MAX_FOOTER: int = ...
    MAX_AUTHOR: int = ...

    _built_pages: List[Embed]
    _max_size: int
    repeat_title: bool
    repeat_desc: bool
    repeat_author: bool

    def __init__(self, **kwargs: Dict[str, ...]) -> None: ...

    def __enter__(self) -> PaginatedEmbed: ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...

    def __iter__(self) -> PaginatedEmbed: ...

    def __next__(self) -> Embed: ...

    @property
    def size(self) -> int: return
    @property
    def num_pages(self) -> int: return
    @property
    def pages(self) -> List[Embed]: return
    @property
    @overload
    def colour(self) -> List[discord.Colour]: return
    @colour.setter
    @overload
    def colour(self, value) -> None: ...

    color = ... # type: property

    @property
    def footer(self) -> EmbedProxy: return
    @property
    def fields(self) -> List[EmbedProxy]: return

    def add_field(self, *, name: str, value: str, inline: bool = ...) -> None: ...

    def to_dict(self) -> Dict[str, ...]: ...

    def close_page(self) -> None: ...

    def close(self) -> None: ...
