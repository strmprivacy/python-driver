import dataclasses
import json
from abc import ABC, abstractmethod
from ctypes import Union
from io import BytesIO

import avro
from avro.io import DatumWriter
from avro.schema import Schema
from avro_json_serializer import AvroJsonSerializer
from jsonschema import validate
from streammachine.schemas.common import StreamMachineEvent

from .type import SerializationType, UnsupportedSerializationTypeException


class EventSerializer(ABC):
    @abstractmethod
    def serialize(self, event: StreamMachineEvent, serialization_type: SerializationType) -> bytes:
        pass


class AvroSerializer(EventSerializer):
    def __init__(self, schema: Schema):
        self._schema: Schema = schema
        self._serializer: Union[DatumWriter, AvroJsonSerializer] = None

    def serialize(self, event: StreamMachineEvent, serialization_type: SerializationType) -> bytes:
        if serialization_type is SerializationType.AVRO_BINARY:
            return self._serialize_avro_binary(event)
        elif serialization_type is SerializationType.AVRO_JSON:
            return self._serialize_avro_json(event)
        else:
            raise UnsupportedSerializationTypeException(
                f"The serialization type {serialization_type} is not supported for Avro")

    def _serialize_avro_binary(self, event_data: object) -> bytes:
        if self._serializer is None or not isinstance(self._serializer, DatumWriter):
            self._serializer = avro.io.DatumWriter(self._schema)

        bytes_writer = BytesIO()
        encoder = avro.io.BinaryEncoder(bytes_writer)
        self._serializer.write(event_data, encoder)
        bytes_writer.flush()

        return bytes_writer.getvalue()

    def _serialize_avro_json(self, event_data: object) -> bytes:
        if self._serializer is None or not isinstance(self._serializer, AvroJsonSerializer):
            self._serializer = AvroJsonSerializer(self._schema)

        return self._serializer.to_json(event_data).encode("utf-8")


class JsonSerializer(EventSerializer):
    # TODO add schema class type
    def __init__(self, schema: dict):
        self._schema = schema

    def serialize(self, event: StreamMachineEvent, _: SerializationType) -> str:
        validate(dataclasses.asdict(event), self._schema)

        return json.dumps(event, cls=JsonSerializer.Encoder)

    class Encoder(json.JSONEncoder):
        def default(self, o):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            return super().default(o)
