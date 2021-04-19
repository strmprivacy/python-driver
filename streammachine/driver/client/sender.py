from aiohttp import ClientSession

from .auth import AuthService
from ..domain import StreamMachineEventDTO
from ..domain.config import ClientConfig


class SenderService(object):
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
        self._session = ClientSession()
        self._requests_to_send = []

    async def start_timer(self):
        await self.auth_service.start()

    async def asend(self, event, serialization_type) -> str:
        dto = StreamMachineEventDTO(event, serialization_type)
        headers = {
            'Authorization': f'Bearer {self.auth_service.get_access_token()}',
            'Content-Type': 'application/octet-stream',
            'Strm-Serialization-Type': dto.get_serialization_type_header(),
            'Strm-Driver-Version': self._config.version.brief_string(),
            'Strm-Driver-Build': self._config.version.release_string(),
            'Strm-Schema-Id': dto.get_schema_id()
        }

        async with self._session.post(self._config.gateway_uri, data=dto.serialize(),
                                      headers=headers) as response:
            response_text = await response.text()

            if response.status != 204:
                self._logger.error(
                    f"Error while sending event to Stream Machine ({self._config.gateway_uri}), response status = {response.status}, response: {response_text}")
            return response.status

    async def close(self):
        await self._session.close()

