
from typing import List, Union, Any, Optional
import datetime as dt
import discord

class PW:

    __slots__ = ('start', 'end', 'members')

    start: dt.datetime
    end: dt.datetime
    members: List['PWMember']

    def __init__(self) -> None: ...

    def get_started(self) -> bool: ...

    def get_finished(self) -> bool: ...

    def begin(self, tz: dt.timezone) -> None: ...

    def finish(self, tz: dt.timezone) -> None: ...

    def join(self, member: discord.Member, tz: dt.timezone) -> bool: ...

    def leave(self, member: discord.Member, tz: dt.timezone) -> bool: ...

class PWMember:

    __slots__ = ('user', 'start', 'end')

    user: discord.Member
    start: dt.datetime
    end: dt.datetime

    def __init__(self, user: discord.Member) -> None: ...

    def __str__(self) -> str: ...

    def __eq__(self, other: Any) -> bool: ...

    def get_len(self) -> Optional[dt.timedelta]: ...

    def get_started(self) -> bool: ...

    def get_finished(self) -> bool: ...

    def begin(self, time: Union[dt.datetime, dt.time]) -> None: ...

    def finish(self, time: Union[dt.datetime, dt.time]) -> None: ...