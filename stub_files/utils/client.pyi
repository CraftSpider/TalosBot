
from typing import Tuple, Optional, Dict, List, Union, overload
from utils.element import Document, Element
import aiohttp
import io

class NanoUser:

    __slots__ = ("client", "username", "_avatar", "_age", "_info", "_novels")

    client: TalosHTTPClient
    username: str
    _avatar: str
    _age: str
    _info: NanoInfo
    _novels: List[NanoNovel]

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

    async def _initialize(self) -> None: ...

    async def _init_novels(self) -> None: ...

class NanoInfo:

    __slots__ = ("bio", "lifetime_stats", "fact_sheet")

    bio: str
    lifetime_stats: Dict[str, str]
    fact_sheet: Dict[str, str]

    def __init__(self, page: Document) -> None: ...

class NanoNovel:

    __slots__ = ("client", "title", "author", "genre", "synopsis", "excerpt", "stats")

    client: TalosHTTPClient
    title: str
    author: NanoUser
    genre: str
    synopsis: str
    excerpt: str
    stats: NanoNovelStats

    async def _initialize(self) -> None: ...

class NanoNovelStats:
    pass

class TalosHTTPClient(aiohttp.ClientSession):

    __slots__ = ("nano_login", "btn_key", "cat_key", "nano_tries")

    NANO_URL: str = ...
    BTN_URL: str = ...
    CAT_URL: str = ...
    XKCD_URL: str = ...
    SMBC_URL: str = ...

    nano_login: Tuple[str, str]
    btn_key: str
    cat_key: str
    nano_tries: int

    # noinspection PyMissingConstructor
    def __init__(self, *args, **kwargs) -> None: ...

    async def get_site(self, url: str, **kwargs) -> Document: ...

    async def btn_get_names(self, gender: str = ..., usage: str = ..., number: int = ..., surname: bool = ...) -> List[str]: ...

    async def nano_get_page(self, url: str) -> Optional[Document]: ...

    async def nano_get_user(self, username: str) -> Optional[NanoUser]: ...

    async def nano_get_novel(self, username: str, title: str = ...) -> NanoNovel: ...

    async def nano_login_client(self) -> int: ...

    async def get_cat_pic(self) -> Dict[str, Union[str, io.BytesIO]]: ...

    async def get_xkcd(self, xkcd: int) -> Dict[str, Union[str, io.BytesIO]]: ...

    async def get_smbc_list(self) -> List[Element]: ...

    async def get_smbc(self, smbc: str) -> Dict[str, Union[str, io.BytesIO]]: ...