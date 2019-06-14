
from typing import NamedTuple, List, Dict, AsyncIterator, Union, NoReturn
import datetime as dt

from utils import TalosHTTPClient, Document


class SimpleNovel(NamedTuple):
    title: str
    genre: str
    words: int

class _Empty:

    def __init_subclass__(cls, **kwargs) -> NoReturn: ...

class NanoUser:

    __slots__ = ("client", "username", "_avatar", "_age", "_info", "_novels", "_simple_novel")

    client: TalosHTTPClient
    username: str
    _avatar: str
    _age: str
    _info: 'NanoInfo'
    _novels: List['NanoNovel']
    _simple_novel: SimpleNovel

    def __init__(self, client: TalosHTTPClient, username: str) -> None: ...

    @property
    async def avatar(self) -> str: ...

    @property
    async def age(self) -> str: ...

    @property
    async def info(self) -> 'NanoInfo': ...

    @property
    async def novels(self) -> List['NanoNovel']: ...

    @property
    async def current_novel(self) -> 'NanoNovel': ...

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
    stats: 'NanoNovelStats'
    _excerpt: str

    def __init__(self, client: TalosHTTPClient, author: NanoUser, nid: str): ...

    @property
    async def excerpt(self): ...

    async def _initialize(self) -> None: ...

class NanoNovelStats:

    __slots__ = ("client", "novel", "_daily_average", "_target", "_target_average", "_total_today", "_total",
                 "_words_remaining", "_current_day", "_days_remaining", "_finish_date", "_average_to_finish")

    client: TalosHTTPClient
    novel: NanoNovel
    _daily_average: int
    _target: int
    _target_average: int
    _total_today: int
    _total: int
    _words_remaining: int
    _current_day: int
    _days_remaining: int
    _finish_date: dt.date
    _average_to_finish: int

    def __init__(self, client: TalosHTTPClient, novel: NanoNovel) -> None: ...

    def __aiter__(self) -> AsyncIterator[Union[int, dt.date]]: ...

    @property
    def author(self) -> NanoUser: ...

    @property
    async def daily_average(self) -> int: ...

    @property
    async def target(self) -> int: ...

    @property
    async def target_average(self) -> int: ...

    @property
    async def total_today(self) -> int: ...

    @property
    async def total(self) -> int: ...

    @property
    async def words_remaining(self) -> int: ...

    @property
    async def current_day(self) -> int: ...

    @property
    async def days_remaining(self) -> int: ...

    @property
    async def finish_date(self) -> dt.date: ...

    @property
    async def average_to_finish(self) -> int: ...

    async def _aiter(self) -> AsyncIterator[Union[int, dt.date]]: ...

    async def _initialize(self) -> None: ...
