from typing import Callable, Any

from .receiver import ReceiverService
from .sender import SenderService
from ..domain import ClientConfig
from ..serializer import SerializationType
from streammachine.schemas.common import StreamMachineEvent


class StreamMachineClient(object):
    def __init__(self, billing_id: str, client_id: str, client_secret: str, config: ClientConfig):
        """
        Class to interact with Stream Machine. For each stream, a separate instance of `StreamMachineClient`
        is required.

        :param billing_id: unique customer identifier
        :param client_id: unique stream identifier
        :param client_secret: secret to authenticate this stream
        :param config: internal configuration (only change if instructed)
        """
        self._sender_service = SenderService(billing_id, client_id, client_secret, config)
        self._receiver_service = ReceiverService(billing_id, client_id, client_secret, config)

    async def start_timers(self):
        await self._sender_service.start_timer()
        await self._receiver_service.start_timer()

    async def send(self, event: StreamMachineEvent, serialization_type: SerializationType) -> str:
        return await self._sender_service.asend(event, serialization_type)

    async def start_receiving_sse(self, as_json: bool, consumer: Callable[[Any], Any]):
        return await self._receiver_service.start(as_json, consumer)

    async def close(self):
        self._receiver_service.close()
