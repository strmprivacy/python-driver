import datetime

import pytz
import requests
from requests import HTTPError

from ..domain.config import ClientConfig
from ..domain.base import JsonSerializable
from ..util import TimerTask


class AuthService(object):
    _headers = {"content-type": "application/json; charset=UTF-8"}

    def __init__(self, purpose: str, billing_id: str, client_id: str, client_secret: str, config: ClientConfig):
        """
        Service responsible for ensuring the validity of access tokens for the Stream Machine Client

        :param purpose: for which is the AuthService initialized
        :param billing_id: unique customer identifier
        :param client_id: unique stream identifier
        :param client_secret: secret to authenticate this stream
        :param config: internal configuration
        """
        self._logger = config.get_logger(__name__)
        self._purpose = purpose
        self._billing_id = billing_id
        self._client_id = client_id
        self._client_secret = client_secret
        self._config = config

        self.auth_provider: AuthProvider = None
        self.timer_task = TimerTask(self._initialize_auth_provider, config.sts_refresh_interval)

    async def start(self):
        await self.timer_task.start()

    def get_access_token(self) -> str:
        return self.auth_provider.id_token

    def _authenticate(self, billing_id: str, client_id: str, client_secret: str) -> None:
        self._logger.debug("authenticate")
        try:
            payload = AuthRequest(billing_id, client_id, client_secret)
            self._do_post(self._config.sts_auth_uri, payload)
        except HTTPError as e:
            self._logger.error(
                f"An error occurred while requesting an access token with clientId '{client_id}' and billingId '{billing_id}'")

    def _refresh(self, refresh_token: str, billing_id: str, client_id: str, client_secret: str) -> None:
        self._logger.debug("_refresh")
        try:
            payload = RefreshRequest(refresh_token)
            self._do_post(self._config.sts_refresh_uri, payload)
        except HTTPError as e:
            self._logger.debug(f"Failed to refresh token with clientId '{client_id}' and billingId '{billing_id}'")
            self._logger.debug(
                f"Trying to request a new token with clientId '{client_id}' and billingId '{billing_id}'")

            self._authenticate(billing_id, client_id, client_secret)

    def _do_post(self, uri: str, payload: JsonSerializable):
        response = None

        try:
            response = requests.post(uri, headers=AuthService._headers, data=payload.to_json())
            self.auth_provider = AuthProvider.from_json(response.json())
        except HTTPError as e:
            self._logger.error(e)
            self._logger.error(response.text)

            raise HTTPError(e, response.text)

    def _initialize_auth_provider(self):
        self._logger.debug("_initialize_auth_provider")
        if self.auth_provider is None:
            self._logger.debug(f"Initializing a new Auth Provider for {self._purpose}")
            self._authenticate(self._billing_id, self._client_id, self._client_secret)
        elif self.auth_provider.is_almost_expired():
            self._logger.debug(f"Refreshing an existing Auth Provider {self._purpose}")
            self._refresh(self.auth_provider.refresh_token, self._billing_id, self._client_id, self._client_secret)


class AuthProvider(JsonSerializable):
    _expiration_slack_time_seconds: int = datetime.timedelta(minutes=10).seconds

    def __init__(self, id_token: str, refresh_token: str, expires_at: int):
        self.id_token = id_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at

    @staticmethod
    def from_json(json_dict: dict) -> 'AuthProvider':
        return JsonSerializable._from_json(json_dict, AuthProvider)

    def is_almost_expired(self):
        current_time = datetime.datetime.now(tz=pytz.utc).timestamp()

        return (current_time + AuthProvider._expiration_slack_time_seconds) >= self.expires_at


class AuthRequest(JsonSerializable):
    def __init__(self, billing_id: str, client_id: str, client_secret: str):
        self.billing_id = billing_id
        self.client_id = client_id
        self.client_secret = client_secret


class RefreshRequest(JsonSerializable):
    def __init__(self, refresh_token: str):
        self.refresh_token = refresh_token
