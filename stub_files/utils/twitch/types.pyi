
from typing import Dict, Any, Set
import datetime as dt

from . import twitch_app


class OAuth:

    app: twitch_app.TwitchApp
    token: str
    _refresh: str
    expiration_time: int
    expires: dt.datetime
    scopes: Set[str]
    type: str

    def __init__(self, data: Dict[str, Any], app: twitch_app.TwitchApp) -> None: ...

    async def validate(self) -> None: ...

    async def refresh(self) -> None: ...

    def _refresh_data(self, data: Dict[str, Any]) -> None: ...

class User:

    __slots__ = ("id", "name", "display_name", "bio", "logo", "created_at", "updated_at", "type")

    id: int
    name: str
    display_name: str
    bio: str
    logo: str
    created_at: int
    updated_at: int
    type: str

    def __init__(self, data: Dict[str, Any]) -> None: ...

    def _refresh_data(self, data: Dict[str, Any]) -> None: ...

class Subscription:

    __slots__ = ("id", "created_at", "sub_plan", "sub_plan_name", "is_gift", "sender", "user")

    id: int
    created_at: int
    sub_plan: str
    sub_plan_name: str
    is_gift: bool
    sender: str
    user: User

    def __init__(self, data: Dict[str, Any]) -> None: ...

    def _refresh_data(self, data: Dict[str, Any]) -> None: ...
