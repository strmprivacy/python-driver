import asyncio
import time
from contextlib import suppress


def current_time_millis():
    return int(round(time.time() * 1000))


class TimerTask(object):
    def __init__(self, method, time_in_seconds):
        """
        Timed repeating task

        :param method: the method to be invoked within this TimerTask
        :param time_in_seconds: frequency of invoking the method
        """
        self.method = method
        self.time_in_seconds = time_in_seconds
        self.running = False
        self._task = None

        self.method()

    async def start(self):
        if not self.running:
            self.running = True
            self._task = asyncio.ensure_future(self._run())

    async def stop(self):
        if self.running:
            self.running = False
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _run(self):
        while True:
            await asyncio.sleep(self.time_in_seconds)
            self.method()
