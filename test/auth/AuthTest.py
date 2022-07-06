import logging
import unittest
from strmprivacy.driver import StrmPrivacyClient, ClientConfig
from strmprivacy.driver.client.auth import AuthService


class AuthTest(unittest.TestCase):
    _CLIENT_ID = "clientId"
    _CLIENT_SECRET = "clientSecret"

    @unittest.skip("To use this test, fill out proper credentials")
    def test_authentication(self):
        config = ClientConfig(logging.INFO, auth_host="accounts.dev.strmprivacy.io")
        auth_service = AuthService("authentication test", self._CLIENT_ID, self._CLIENT_SECRET, config)
        access_token = auth_service.get_access_token()
        assert access_token != ""

    @unittest.skip("To use this test, fill out proper credentials")
    def test_refresh(self):
        config = ClientConfig(logging.INFO, auth_host="accounts.dev.strmprivacy.io")
        auth_service = AuthService("authentication test", self._CLIENT_ID, self._CLIENT_SECRET, config)
        access_token_before = auth_service.get_access_token()
        refresh_token = auth_service.get_refresh_token()
        auth_service._refresh(refresh_token, self._CLIENT_ID, self._CLIENT_SECRET)
        access_token_after = auth_service.get_access_token()
        assert access_token_after != "", "Access token is empty"
        assert access_token_before != access_token_after, "Access token has not refreshed"
