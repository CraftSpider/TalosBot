
from typing import Callable, Awaitable, Any, Optional, Union
import asyncio
import utils
import utils.dutils as dutils
import datetime as dt


def align_period(period: utils.EventPeriod) -> dt.timedelta: ...

class EventLoop:

    __slots__ = ("_task", "_callback", "period", "persist", "start_time", "loop", "name", "parent")

    _task: asyncio.Task
    _callback: Callable[[Any], Awaitable]
    period: utils.EventPeriod
    persist: bool
    start_time: Optional[dt.datetime]
    loop: asyncio.AbstractEventLoop
    name: str
    parent: Union[utils.TalosCog, dutils.ExtendedBot]

    @property
    def callback(self) -> Callable[[Any], Awaitable]: ...

    @callback.setter
    def callback(self, value: Callable[[Any], Awaitable]) -> None: ...

    def set_start_time(self, time: dt.datetime) -> None: ...

    def start(self, *args: Any, **kwargs: Any) -> None: ...

    async def run(self, *args: Any, **kwargs: Any) -> None: ...

    def stop(self) -> None: ...

def eventloop(period: Union[str, utils.EventPeriod], *, persist: bool = ..., start_time: dt.datetime = ...) -> Callable[[Callable[[Any], Awaitable]], EventLoop]: ...