
import datetime as dt
import asyncio
import logging
import inspect

from .. import data, utils
from . import errors


log = logging.getLogger("talos.dutils.events")


def align_period(period):
    now = dt.datetime.now()
    days = 0
    hours = 0
    minutes = 0
    seconds = 0
    if period.days:
        hours = 24 - now.hour
        minutes = 60 - now.minute
        seconds = 60 - now.second
    elif period.hours:
        minutes = 60 - now.minute
        seconds = 60 - now.second
    elif period.minutes:
        seconds = 60 - now.second

    days += period.days - 1 if period.days else 0
    hours += period.hours - 1 if period.hours else 0
    minutes += period.minutes - 1 if period.minutes else 0
    seconds += period.seconds - 1 if period.seconds else 0

    return dt.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


class EventLoop:

    __slots__ = ("_task", "_callback", "_instance", "period", "persist", "start_time", "loop", "name", "parent",
                 "description")

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Access internal method through self.callback")

    def __init__(self, coro, period, loop=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._task = None
        self._callback = coro
        self.description = inspect.cleandoc(kwargs.get("description"))
        self.period = data.EventPeriod(period)
        self.persist = kwargs.get("persist")
        self.start_time = kwargs.get("start_time")
        self.name = kwargs.get("name", coro.__name__)
        self.loop = loop
        self.parent = None

    def __str__(self):
        return f"EventLoop(period: {self.period}, name: {self.name}, description: {self.description})"

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, value):
        self._callback = value

    def set_start_time(self, time):
        self.start_time = time

    def start(self, *args, **kwargs):
        log.info(f"Starting event loop {self.name}")
        if self.parent is not None:
            newargs = [self.parent]
            newargs.extend(args)
            args = tuple(newargs)
        self._task = self.loop.create_task(self.run(*args, **kwargs))

    async def run(self, *args, **kwargs):
        if self.start_time is not None:
            now = dt.datetime.utcnow()
            delta = self.start_time - now
            await asyncio.sleep(delta.total_seconds())
        else:
            delta = align_period(self.period)
            await asyncio.sleep(delta.total_seconds())
        while True:
            try:
                log.debug(f"Running event loop {self.name}")
                await self._callback(*args, **kwargs)
            except errors.StopEventLoop as e:
                if e.message:
                    log.warning(e.message)
                return
            except Exception as e:
                if self.persist:
                    utils.log_error(log, logging.WARNING, e, f"Ignoring error in event loop {self.name}:")
                else:
                    utils.log_error(log, logging.ERROR, e, f"Stopping event loop {self.name}:")
                    self._task = None
                    return
            delta = align_period(self.period)
            await asyncio.sleep(delta.total_seconds())

    def stop(self):
        if self._task is not None:
            self._task.cancel()


def eventloop(period, **kwargs):

    def decorator(coro):
        return EventLoop(coro, period, **kwargs)

    return decorator
