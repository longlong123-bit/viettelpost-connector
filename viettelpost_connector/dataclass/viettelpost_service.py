from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Sequence, Tuple
from .dictionary_io import InputDict, OutputDict


class KEY_INPUT_DICT_SERVICE(Enum):
    CODE: str = 'SERVICE_CODE'
    NAME: str = 'SERVICE_NAME'


class KEY_OUTPUT_DICT_SERVICE(Enum):
    CODE: str = 'code'
    NAME: str = 'name'


class KEY_INPUT_DICT_SERVICE_EXTEND(Enum):
    CODE: str = 'SERVICE_CODE'
    NAME: str = 'SERVICE_NAME'


class KEY_OUTPUT_DICT_SERVICE_EXTEND(Enum):
    SERVICE_ID: str = 'service_id'
    CODE: str = 'extend_code'
    NAME: str = 'extend_name'


@dataclass(frozen=True)
class Service(InputDict, OutputDict):
    code: str
    name: str

    @staticmethod
    def parser_dict(data: Dict[str, Any]) -> Sequence[Tuple]:
        result: tuple = (
            data.get(KEY_INPUT_DICT_SERVICE.CODE.value),
            data.get(KEY_INPUT_DICT_SERVICE.NAME.value)
        )
        return result

    @staticmethod
    def parser_class(cls, **kwargs) -> Dict[str, Any]:
        payload: dict = {
            KEY_OUTPUT_DICT_SERVICE.CODE.value: cls.code,
            KEY_OUTPUT_DICT_SERVICE.NAME.value: cls.name
        }
        return payload


@dataclass(frozen=True)
class ServiceExtend(InputDict, OutputDict):
    code: str
    name: str

    @staticmethod
    def parser_dict(data: Dict[str, Any]) -> Sequence[Tuple]:
        result: tuple = (
            data.get(KEY_INPUT_DICT_SERVICE_EXTEND.CODE.value),
            data.get(KEY_INPUT_DICT_SERVICE_EXTEND.NAME.value)
        )
        return result

    @staticmethod
    def parser_class(cls, **kwargs) -> Dict[str, Any]:
        payload: dict = {
            KEY_OUTPUT_DICT_SERVICE_EXTEND.CODE.value: cls.code,
            KEY_OUTPUT_DICT_SERVICE_EXTEND.NAME.value: cls.name,
            KEY_OUTPUT_DICT_SERVICE_EXTEND.SERVICE_ID.value: kwargs.get(KEY_OUTPUT_DICT_SERVICE_EXTEND.SERVICE_ID.value)
        }
        return payload
