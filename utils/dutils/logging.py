
import asyncio
import logging


class DiscordLogger(logging.Handler):

    def __init__(self, ctx, level=logging.NOTSET, *, loop=None):
        super().__init__(level)
        self.channel = ctx.channel
        if loop is None:
            loop = ctx.bot.loop
        self.loop = loop
        self.queue = asyncio.Queue()
        self.running = True
        self.loop.create_task(self._run_loop())

    async def _run_loop(self):
        while self.running:
            record = await self.queue.get()
            log = self.format(record)
            await self.channel.send(log)
            await asyncio.sleep(1)

    def emit(self, record):
        self.queue.put_nowait(record)

    def stop(self):
        self.running = False
