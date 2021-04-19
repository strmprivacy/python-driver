import json
from typing import Dict


class JsonSerializable(object):
    @staticmethod
    def _from_json(json_dict: Dict, clazz):
        return clazz(**JsonSerializable._to_snake_case(json_dict))

    def to_json(self):
        return json.dumps(self, default=self._to_camel_case)

    def _to_camel_case(self, obj):
        return {JsonSerializable.snake_case_to_camel_case(k): v for k, v in obj.__dict__.items()}

    @staticmethod
    def _to_snake_case(json_dict: Dict):
        return {JsonSerializable.camel_case_to_snake_case(k): v for k, v in json_dict.items()}

    @staticmethod
    def snake_case_to_camel_case(s):
        parts = s.split('_')
        return parts[0] + ''.join(part.title() for part in parts[1:])

    @staticmethod
    def camel_case_to_snake_case(s):
        return ''.join(['_' + c.lower() if c.isupper() else c for c in s]).lstrip('_')
