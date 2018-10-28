
import datetime as dt
import asyncio
import logging

from .. import data


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


class StopEventLoop(Exception):

    __slots__ = ("message",)

    def __init__(self, message=None):
        super().__init__(message)
        self.message = message


class EventLoop:

    __slots__ = ("_task", "_callback", "_instance", "period", "persist", "start_time", "loop", "name", "parent")

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Access internal method through self.callback")

    def __init__(self, coro, period, *, persist=True, start_time=None, name=None, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._task = None
        self._callback = coro
        self.period = data.EventPeriod(period)
        self.persist = persist
        self.start_time = start_time
        self.name = name if name is not None else coro.__name__
        self.loop = loop
        self.parent = None

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
            now = dt.datetime.now()
            delta = self.start_time - now
            await asyncio.sleep(delta.total_seconds())
        else:
            delta = align_period(self.period)
            await asyncio.sleep(delta.total_seconds())
        while True:
            try:
                log.debug(f"Running event loop {self.name}")
                await self._callback(*args, **kwargs)
            except StopEventLoop as e:
                if e.message:
                    log.warning(e.message)
                return
            except Exception as e:
                if self.persist:
                    log.warning(f"Ignoring error in event loop {self.name}: {e}")
                else:
                    log.error(f"Stopping event loop {self.name}: {e}")
                    self._task = None
                    return
            delta = align_period(self.period)
            await asyncio.sleep(delta.total_seconds())

    def stop(self):
        self._task.cancel()


def eventloop(period, *, persist=True, start_time=None, name=None):

    def decorator(coro):
        return EventLoop(coro, period, persist=persist, start_time=start_time, name=name)

    return decorator
