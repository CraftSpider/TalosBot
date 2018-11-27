
import datetime as dt
import asyncio
import logging
import inspect

from .. import data, utils
from . import errors


log = logging.getLogger("talos.dutils.events")


def align_period(period):
    """
        Align a period for its next execution. From now, push forward the period, then down to the nearest 0.
    :param period: Period to return alignment for
    :return: delta till when period should next run
    """
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
    """
        Conceptually, an event that should be run every X length of time. Takes an asynchronous function,
        and runs it once for every passing of period length of time.
    """

    __slots__ = ("_task", "_callback", "_instance", "period", "persist", "start_time", "loop", "name", "parent",
                 "description", "long_desc")

    def __call__(self, *args, **kwargs):
        """
            An attempt to directly call an EventLoop should fail
        """
        raise NotImplementedError("Access internal method through self.callback")

    def __init__(self, coro, period, loop=None, **kwargs):
        """
            Initialize an eventloop object with a coroutine and period at least
        :param coro: Internal coroutine object
        :param period: Interval between calls
        :param loop: asyncio event loop, if None uses default
        :param kwargs: Other parameters. Description, persist (whether to ignore errors), start_time, and name.
                       If name is not provided, then coro.__name__ is used instead
        """
        if loop is None:
            loop = asyncio.get_event_loop()
        self._task = None
        self._callback = coro
        self.description = inspect.cleandoc(kwargs.get("description"))
        self.long_desc = inspect.cleandoc(kwargs.get("long_desc", inspect.getdoc(coro)))
        self.period = data.EventPeriod(period)
        self.persist = kwargs.get("persist")
        self.start_time = kwargs.get("start_time")
        self.name = kwargs.get("name", coro.__name__)
        self.loop = loop
        self.parent = None

    def __str__(self):
        """
            Convert this eventloop to a string representation, containing the period, name, and short description
        :return: String form of loop
        """
        return f"EventLoop(period: {self.period}, name: {self.name}, description: {self.description})"

    @property
    def callback(self):
        """
            Retrieve the internal callback object
        :return: Internal coro
        """
        return self._callback

    @callback.setter
    def callback(self, value):
        """
            Set the internal callback object
        :param value: Callback to set
        """
        self._callback = value

    def set_start_time(self, time):
        """
            Set the EventLoop start time. While event loop is running, this won't change anything
        :param time: datetime to start the loop at
        :return:
        """
        self.start_time = time

    def start(self, *args, **kwargs):
        """
            Start the EventLoop, creating a task and adding it to the loop
        :param args: Arguments to run the loop with
        :param kwargs: Keyword arguments to run the loop with
        """
        log.info(f"Starting event loop {self.name}")
        if self.parent is not None:
            newargs = [self.parent]
            newargs.extend(args)
            args = tuple(newargs)
        self._task = self.loop.create_task(self.run(*args, **kwargs))

    async def run(self, *args, **kwargs):
        """
            Actual runner of the EventLoop. Aligns the periods, and does error handling. Should propagate no Exceptions,
            though warnings or errors will be logged on persist or killing error.
        :param args: Arguments to run the loop with
        :param kwargs: Keyword arguments to run the loop with
        """
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
        """
            Stop the EventLoop. Cancels the task, does any cleanup
        """
        if self._task is not None:
            log.info(f"Stopping event loop {self.name}")
            self._task.cancel()
            self._task = None


def eventloop(period, **kwargs):
    """
        Decorator to turn a coroutine into an EventLoop
    :param period: Length of time between loop repititions, generally a string like 1m3s
    :param kwargs: Arguments to pass to the EventLoop constructor
    :return: Internal callback
    """

    def decorator(coro):
        return EventLoop(coro, period, **kwargs)

    return decorator
