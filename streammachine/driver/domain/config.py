import logging

from pbr.version import SemanticVersion

from .. import __version__


class ClientConfig(object):
    def __init__(self, log_level=logging.INFO, **kwargs):
        self._log_level = log_level
        self._gateway_protocol = kwargs.get("gateway_protocol", "https")
        self._gateway_host = kwargs.get("gateway_host", "in.strm.services")
        self._gateway_endpoint = kwargs.get("gateway_endpoint", "/event")
        self._egress_protocol = kwargs.get("egress_protocol", "https")
        self._egress_host = kwargs.get("egress_host", "out.strm.services")
        self._egress_endpoint = kwargs.get("egress_endpoint", "/ws")
        self._egress_health_endpoint = kwargs.get("egress_health_endpoint", "/is-alive")
        self._sts_protocol = kwargs.get("sts_protocol", "https")
        self._sts_host = kwargs.get("sts_host", "auth.strm.services")
        self._sts_auth_endpoint = kwargs.get("sts_auth_endpoint", "/auth")
        self._sts_refresh_endpoint = kwargs.get("sts_refresh_endpoint", "/refresh")
        self._sts_refresh_interval = kwargs.get("sts_refresh_interval", 3300)
        self._version = SemanticVersion.from_pip_string(__version__)

    def get_logger(self, name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(self._log_level)
        return logger

    @property
    def gateway_uri(self):
        return f"{self._gateway_protocol}://{self._gateway_host}{self._gateway_endpoint}"

    @property
    def egress_uri(self):
        return f"{self._egress_protocol}://{self._egress_host}{self._egress_endpoint}"

    @property
    def egress_health_uri(self):
        return f"{self._egress_protocol}://{self._egress_host}{self._egress_health_endpoint}"

    @property
    def sts_auth_uri(self):
        return f"{self._sts_protocol}://{self._sts_host}{self._sts_auth_endpoint}"

    @property
    def sts_refresh_uri(self):
        return f"{self._sts_protocol}://{self._sts_host}{self._sts_refresh_endpoint}"

    @property
    def sts_refresh_interval(self):
        return self._sts_refresh_interval

    @property
    def version(self) -> SemanticVersion:
        return self._version
