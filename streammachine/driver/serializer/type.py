from enum import Enum


class SerializationType(Enum):
    AVRO_BINARY = 1
    AVRO_JSON = 2
    JSON = 3


class UnsupportedSerializationTypeException(Exception):
    pass
