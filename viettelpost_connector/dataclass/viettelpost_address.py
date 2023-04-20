from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Sequence, Tuple
from .dictionary_io import InputDict, OutputDict


class KEY_INPUT_DICT_PROVINCE(Enum):
    ID: str = 'PROVINCE_ID'
    CODE: str = 'PROVINCE_CODE'
    NAME: str = 'PROVINCE_NAME'


class KEY_OUTPUT_DICT_PROVINCE(Enum):
    ID: str = 'province_id'
    CODE: str = 'province_code'
    NAME: str = 'province_name'


class KEY_INPUT_DICT_DISTRICT(Enum):
    ID: str = 'DISTRICT_ID'
    CODE: str = 'DISTRICT_VALUE'
    NAME: str = 'DISTRICT_NAME'
    PROVINCE_ID: str = 'PROVINCE_ID'


class KEY_OUTPUT_DICT_DISTRICT(Enum):
    ID: str = 'district_id'
    CODE: str = 'district_code'
    NAME: str = 'district_name'
    PROVINCE_ID: str = 'province_id'


class KEY_INPUT_DICT_WARD(Enum):
    ID: str = 'WARDS_ID'
    NAME: str = 'WARDS_NAME'
    DISTRICT_ID: str = 'DISTRICT_ID'


class KEY_OUTPUT_DICT_WARD(Enum):
    ID: str = 'ward_id'
    NAME: str = 'ward_name'
    DISTRICT_ID: str = 'district_id'


@dataclass(frozen=True)
class Province(InputDict, OutputDict):
    id: int
    code: str
    name: str

    @staticmethod
    def parser_dict(data: Dict[str, Any]) -> Sequence[Tuple]:
        result: tuple = (
            data.get(KEY_INPUT_DICT_PROVINCE.ID.value),
            data.get(KEY_INPUT_DICT_PROVINCE.CODE.value),
            data.get(KEY_INPUT_DICT_PROVINCE.NAME.value)
        )
        return result

    @staticmethod
    def parser_class(cls, **kwargs) -> Dict[str, Any]:
        payload: dict = {
            KEY_OUTPUT_DICT_PROVINCE.ID.value: cls.id,
            KEY_OUTPUT_DICT_PROVINCE.CODE.value: cls.code,
            KEY_OUTPUT_DICT_PROVINCE.NAME.value: cls.name
        }
        return payload


@dataclass(frozen=True)
class District(InputDict, OutputDict):
    id: int
    code: str
    name: str
    province_id: int

    @staticmethod
    def parser_dict(data: Dict[str, Any]) -> Sequence[Tuple]:
        result: tuple = (
            data.get(KEY_INPUT_DICT_DISTRICT.ID.value),
            data.get(KEY_INPUT_DICT_DISTRICT.CODE.value),
            data.get(KEY_INPUT_DICT_DISTRICT.NAME.value).title(),
            data.get(KEY_INPUT_DICT_DISTRICT.PROVINCE_ID.value)
        )
        return result

    @staticmethod
    def parser_class(cls, **kwargs) -> Dict[str, Any]:
        payload: dict = {
            KEY_OUTPUT_DICT_DISTRICT.ID.value: cls.id,
            KEY_OUTPUT_DICT_DISTRICT.CODE.value: cls.code,
            KEY_OUTPUT_DICT_DISTRICT.NAME.value: cls.name,
            KEY_OUTPUT_DICT_DISTRICT.PROVINCE_ID.value: kwargs.get(KEY_OUTPUT_DICT_DISTRICT.PROVINCE_ID.value)
        }
        return payload


@dataclass(frozen=True)
class Ward(InputDict, OutputDict):
    id: int
    name: str
    district_id: int

    @staticmethod
    def parser_dict(data: Dict[str, Any]) -> Sequence[Tuple]:
        result: tuple = (
            data.get(KEY_INPUT_DICT_WARD.ID.value),
            data.get(KEY_INPUT_DICT_WARD.NAME.value).title(),
            data.get(KEY_INPUT_DICT_WARD.DISTRICT_ID.value)
        )
        return result

    @staticmethod
    def parser_class(cls, **kwargs) -> Dict[str, Any]:
        payload: dict = {
            KEY_OUTPUT_DICT_WARD.ID.value: cls.id,
            KEY_OUTPUT_DICT_WARD.NAME.value: cls.name,
            KEY_OUTPUT_DICT_WARD.DISTRICT_ID.value: kwargs.get(KEY_OUTPUT_DICT_WARD.DISTRICT_ID.value)
        }
        return payload
