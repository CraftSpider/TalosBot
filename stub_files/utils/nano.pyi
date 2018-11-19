
from typing import NamedTuple, List, Dict
from utils import TalosHTTPClient, Document


class SimpleNovel(NamedTuple):
    title: str
    genre: str
    words: int

class NanoUser:

    __slots__ = ("client", "username", "_avatar", "_age", "_info", "_novels", "_simple_novel")

    client: TalosHTTPClient
    username: str
    _avatar: str
    _age: str
    _info: NanoInfo
    _novels: List[NanoNovel]
    _simple_novel: NamedTuple

    def __init__(self, client: TalosHTTPClient, username: str) -> None: ...

    @property
    async def avatar(self) -> str: ...

    @property
    async def age(self) -> str: ...

    @property
    async def info(self) -> NanoInfo: ...

    @property
    async def novels(self) -> List[NanoNovel]: ...

    @property
    async def current_novel(self) -> NanoNovel: ...

    @property
    async def simple_novel(self) -> SimpleNovel: ...

    async def _initialize(self) -> None: ...

    async def _init_novels(self) -> None: ...

class NanoInfo:

    __slots__ = ("bio", "lifetime_stats", "fact_sheet")

    bio: str
    lifetime_stats: Dict[str, str]
    fact_sheet: Dict[str, str]

    def __init__(self, page: Document) -> None: ...

class NanoNovel:

    __slots__ = ("client", "id", "author", "year", "title", "genre", "cover", "winner", "synopsis", "stats", "_excerpt")

    client: TalosHTTPClient
    id: str
    author: NanoUser
    year: int
    title: str
    genre: str
    cover: str
    winner: bool
    synopsis: str
    stats: NanoNovelStats
    _excerpt: str

    def __init__(self, client: TalosHTTPClient, author: NanoUser, nid: str): ...

    @property
    async def excerpt(self): ...

    async def _initialize(self) -> None: ...

class NanoNovelStats:
    pass