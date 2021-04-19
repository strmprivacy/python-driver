from typing import Callable, Any

import aiohttp
from aiohttp import ClientSession

from .auth import AuthService
from ..domain import ClientConfig


class ReceiverService(object):
    def __init__(self, billing_id: str, client_id: str, client_secret: str, config: ClientConfig):
        self._logger = config.get_logger(__name__)

        self.auth_service = AuthService(
            purpose=self.__class__.__name__,
            billing_id=billing_id,
            client_id=client_id,
            client_secret=client_secret,
            config=config
        )

        self._config = config
        self._client = None
        self._running = False
        self._session = ClientSession()

    async def start_timer(self):
        await self.auth_service.start()

    async def start(self, as_json: bool, consumer: Callable[[Any], Any]):
        self._running = True

        await self.auth_service.start()
        uri = self._config.egress_uri + ("?asJson=true" if as_json else "")

        while self._running:
            async with self._session.ws_connect(uri, headers={
                'Authorization': f'Bearer {self.auth_service.get_access_token()}',
                'Strm-Driver-Version': self._config.version.brief_string(),
                'Strm-Driver-Build': self._config.version.release_string()
            }) as ws:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        await consumer(msg.data)
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        self._logger.debug("Websocket connection closed")
                        break
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        self._logger.debug("Error upon receiving data from websocket")
                        break

    def close(self):
        self._running = False
