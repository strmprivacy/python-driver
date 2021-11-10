import asyncio
import json
import re
import unittest

import responses

from strmprivacy.driver import SerializationType, StrmPrivacyClient, ClientConfig
from test.test_util import TestData


class StrmPrivacyClientTest(unittest.TestCase):
    _BILLING_ID = "robin5"
    _CLIENT_ID = "8xkz4x63rfqfvc5b97oq2ej1gzidqa"
    _CLIENT_SECRET = "4NZD3#cWeGG_X0FpR%kfGwKJNQJLBZ"

    _PARAMETERS = [
        # {'name': 'avro_binary', 'serialization_type': SerializationType.AVRO_BINARY, 'event': TestData.create_avro_event()},
        # {'name': 'avro_json', 'serialization_type': SerializationType.AVRO_JSON, 'event': TestData.create_avro_event()},
        {'name': 'json', 'serialization_type': SerializationType.JSON, 'event': TestData.create_json_event()}
    ]

    # @responses.activate
    def test_send_events(self):
        StrmPrivacyClientTest.setup_auth_mockserver()

        for parameters in StrmPrivacyClientTest._PARAMETERS:
            with self.subTest(msg=parameters['name']):
                # Given an event
                client = StrmPrivacyClient(
                    StrmPrivacyClientTest._BILLING_ID,
                    StrmPrivacyClientTest._CLIENT_ID,
                    StrmPrivacyClientTest._CLIENT_SECRET,
                    ClientConfig()
                )
                event = parameters['event']
                serialization_type = parameters['serialization_type']

                # When the event is sent
                loop = asyncio.new_event_loop()
                request = client.send(event, serialization_type)
                response = loop.run_until_complete(request)
                loop.close()

                # Then the response should match ok
                self.assertEqual("ok", response)

    def test_receive_events(self):
        client = StrmPrivacyClient(
            'robin5',
            '7vbcwbpdf6maj8uffp5mo7743yaazz',
            'iS@yD8Dq5@OAFTDdMs&hGOjWHD%aOI',
            ClientConfig()
        )

        while True:
            client.start_receiving_ws(True, lambda message: print(message))

    @staticmethod
    def setup_auth_mockserver():
        """
        If you want to use this mockserver, enable it adding @responses.activate to a method
        """
        responses.add_passthru(re.compile('.*localhost.*'))
        responses.add(
            responses.POST,
            "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=",
            status=200,
            body=json.dumps({
                'kind': 'identitytoolkit#VerifyPasswordResponse',
                'localId': 'id',
                'email': 'test@strm.in',
                'displayName': '',
                'idToken': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vc3RyZWFtLW1hY2hpbmUtMjc5MDExIiwiaWF0IjoxNTk0ODExOTM1LCJleHAiOjE2MjYzNDc5MzUsImF1ZCI6InN0cmVhbS1tYWNoaW5lLTI3OTAxMSIsInN1YiI6IjBaM2c0ZHBWdEFPeGtQUFdoVG11bTJ0ZHJ1ZzEiLCJlbWFpbCI6InN0cm0tc3RyZWFtaW4tYXJvdW5kQHN0cm0tYmFuYW5hLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjoidHJ1ZSJ9.bzzvOAS5kwy7GsnVcMu7BFCK8mMDD6NI1C4Ed3i6o6A',
                'registered': True,
                'refreshToken': 'banaan',
                'expiresIn': '3600'
            }),
            adding_headers={
                'Content-Type': 'application/json; charset=utf-8'
            }
        )
