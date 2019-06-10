
import asyncio
import logging


class DiscordHandler(logging.Handler):
    """
        Handler to allow the builtin python logger to log to discord. Requires a context object be provided
        for the handler to know where to log to. The logger starts an asyncio constantly running task, so is
        not the most efficient. Primarily should be used for debug
    """

    def __init__(self, ctx, level=logging.NOTSET, *, loop=None):
        """
            Create a new DiscordHandler, pointing to a specific context
        :param ctx: Context to use
        :param level: Level to log at, by default
        :param loop: Loop to use, if different from ctx.bot.loop
        """
        super().__init__(level)
        self.channel = ctx.channel
        if loop is None:
            loop = ctx.bot.loop
        self.loop = loop
        self.queue = asyncio.Queue()
        self.running = True
        self.loop.create_task(self._run_loop())

    async def _run_loop(self):
        """
            The primary execution loop. Prints a new log message every second, to avoid spamming the endpoint
            Draws from the internal record queue
        """
        while self.running:
            record = await self.queue.get()
            log = self.format(record)
            await self.channel.send(log)
            await asyncio.sleep(1)

    def emit(self, record):
        """
            Add a new log to be logged. Places the record into the internal queue, to be removed by the run loop
        :param record: Record to log
        """
        self.queue.put_nowait(record)

    def stop(self):
        """
            Stop running this logger immediately, killing the run loop so things can easily be cleaned up
        """
        self.running = False
