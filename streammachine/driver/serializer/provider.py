from .type import UnsupportedSerializationTypeException
from ...driver.serializer import AvroSerializer, EventSerializer, JsonSerializer


class SerializationProvider(object):
    _serializers = dict()

    def __init__(self):
        raise NotImplementedError(
            "SerializationProvider is not meant to be instantiated. Use the static methods instead.")

    @staticmethod  # TODO add schema class type
    def get_serializer(schema_id: str, schema_type: str, schema) -> EventSerializer:
        existing_serializer = SerializationProvider._serializers.get(schema_id)

        if existing_serializer is None:
            if schema_type == "avro":
                serializer = AvroSerializer(schema)

                SerializationProvider._serializers[schema_id] = serializer

                return serializer
            elif schema_type == "json":
                serializer = JsonSerializer(schema)

                SerializationProvider._serializers[schema_id] = serializer

                return serializer
            else:
                raise UnsupportedSerializationTypeException(f"Provided schema type '{schema_type}' is not supported")

        return existing_serializer
