import asyncio
import logging
import time
from threading import Thread

import janus

from .. import StreamMachineClient, SerializationType
from ..domain.config import ClientConfig


class SyncSender(Thread):
    """
    A thread that owns an async event loop, and that receives events on a Janus queue from the synchronous
    part of the application. So this thing sends asynchronously, but can be called safely from multiple
    synchronous threads.

    If you use this class, `janus` needs to be added to the dependencies.
    """

    def __init__(self, billing_id, client_id, client_secret, log_level=logging.DEBUG, async_debug=False):
        Thread.__init__(self)
        self._config = ClientConfig(log_level=logging.DEBUG)
        self._props = (billing_id, client_id, client_secret)
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(log_level)
        self._queue = None
        self.async_debug = async_debug

    def run(self):
        """
        Start the event loop that handles the messages on the Janus queue
        :return:
        """
        asyncio.run(self.async_start(*self._props), debug=self.async_debug)

    async def async_start(self, billing_id, client_id, client_secret):
        self._queue = janus.Queue()
        client = StreamMachineClient(billing_id, client_id, client_secret, self._config)
        await client.start_timers()  # for the re-authorization jwt timer
        while True:
            event, serialization_type = await self._queue.async_q.get()
            await client.send(event, serialization_type)

    def wait_ready(self):
        """
        wait for the queue to become available
        :return:
        """
        while True:
            if self._queue is not None:
                return
            time.sleep(0.01)

    def send_event(self, event, serialization_type=SerializationType.AVRO_BINARY):
        self._queue.sync_q.put((event, serialization_type))
