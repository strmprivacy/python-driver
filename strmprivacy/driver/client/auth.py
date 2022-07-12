import datetime

import pytz
import requests
from requests import HTTPError

from ..domain.config import ClientConfig
from ..domain.base import JsonSerializable
from ..util import TimerTask


class AuthService(object):
    _headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"}

    def __init__(self, purpose: str, client_id: str, client_secret: str, config: ClientConfig):
        """
        Service responsible for ensuring the validity of access tokens for the StrmPrivacyClient

        :param purpose: for which is the AuthService initialized
        :param client_id: unique stream identifier
        :param client_secret: secret to authenticate this stream
        :param config: internal configuration
        """
        self._logger = config.get_logger(__name__)
        self._purpose = purpose
        self._client_id = client_id
        self._client_secret = client_secret
        self._config = config

        self.auth_provider: AuthProvider = None
        self.timer_task = TimerTask(self._initialize_auth_provider, config.auth_refresh_interval)

    async def start(self):
        await self.timer_task.start()

    def get_access_token(self) -> str:
        return self.auth_provider.access_token

    def get_refresh_token(self) -> str:
        return self.auth_provider.refresh_token

    def _authenticate(self, client_id: str, client_secret: str) -> None:
        self._logger.debug("authenticate")
        try:
            payload = f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}"
            self._do_post(self._config.auth_auth_uri, payload)
        except HTTPError as e:
            self._logger.error(
                f"An error occurred while requesting an access token with clientId '{client_id}'")

    def _refresh(self, refresh_token: str, client_id: str, client_secret: str) -> None:
        self._logger.debug("_refresh")
        try:
            payload = f"grant_type=refresh_token&client_id={client_id}&" \
                      f"client_secret={client_secret}&refresh_token={refresh_token}"
            self._do_post(self._config.auth_auth_uri, payload)
        except HTTPError as e:
            self._logger.debug(f"Failed to refresh token with clientId '{client_id}'")
            self._logger.debug(
                f"Trying to request a new token with clientId '{client_id}'")

            self._authenticate(client_id, client_secret)

    def _do_post(self, uri: str, payload: str):
        response = None

        try:
            response = requests.post(uri, headers=AuthService._headers, data=payload)
            self.auth_provider = AuthProvider.from_json(response.json())
        except HTTPError as e:
            self._logger.error(e)
            self._logger.error(response.text)

            raise HTTPError(e, response.text)

    def _initialize_auth_provider(self):
        self._logger.debug("_initialize_auth_provider")
        if self.auth_provider is None:
            self._logger.debug(f"Initializing a new Auth Provider for {self._purpose}")
            self._authenticate(self._client_id, self._client_secret)
        elif self.auth_provider.is_almost_expired():
            self._logger.debug(f"Refreshing an existing Auth Provider {self._purpose}")
            self._refresh(self.auth_provider.refresh_token, self._client_id, self._client_secret)


class AuthProvider(JsonSerializable):
    _expiration_slack_time_seconds: int = datetime.timedelta(minutes=10).seconds

    def __init__(self, access_token: str, refresh_token: str, expires_in: int, **kwargs):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in
        self.expires_at = datetime.datetime.now(tz=pytz.utc).timestamp() + expires_in

    @staticmethod
    def from_json(json_dict: dict) -> 'AuthProvider':
        return JsonSerializable._from_json(json_dict, AuthProvider)

    def is_almost_expired(self):
        current_time = datetime.datetime.now(tz=pytz.utc).timestamp()

        return (current_time + AuthProvider._expiration_slack_time_seconds) >= self.expires_at


class AuthRequest(JsonSerializable):
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret


class RefreshRequest(JsonSerializable):
    def __init__(self, refresh_token: str):
        self.refresh_token = refresh_token
