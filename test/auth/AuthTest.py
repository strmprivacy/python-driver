import logging
import unittest
from strmprivacy.driver import StrmPrivacyClient, ClientConfig
from strmprivacy.driver.client.auth import AuthService


class AuthTest(unittest.TestCase):
    _CLIENT_ID = "clientId"
    _CLIENT_SECRET = "clientSecret"

    @unittest.skip
    def test_authentication(self):
        config = ClientConfig(logging.INFO, keycloak_host="accounts.dev.strmprivacy.io")
        auth_service = AuthService("authentication test", self._CLIENT_ID, self._CLIENT_SECRET, config)
        access_token = auth_service.get_access_token()
        assert access_token != ""
