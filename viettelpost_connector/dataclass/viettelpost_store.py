from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Sequence, Tuple
from .dictionary_io import InputDict, OutputDict


class KEY_INPUT_DICT_STORE(Enum):
    GROUP_ADDRESS_ID: str = 'groupaddressId'
    CUS_ID: str = 'cusId'
    NAME: str = 'name'
    PHONE: str = 'phone'
    ADDRESS: str = 'address'
    PROVINCE_ID: str = 'provinceId'
    DISTRICT_ID: str = 'districtId'
    WARDS_ID: str = 'wardsId'


class KEY_OUTPUT_DICT_STORE(Enum):
    NAME: str = 'name'
    PHONE: str = 'phone'
    GROUP_ADDRESS_ID: str = 'group_address_id'
    CUS_ID: str = 'customer_id'
    ADDRESS: str = 'address'
    PROVINCE_ID: str = 'province_id'
    DISTRICT_ID: str = 'district_id'
    WARD_ID: str = 'ward_id'


@dataclass(frozen=True)
class Store(InputDict, OutputDict):
    name: str
    phone: str
    group_address_id: int
    cus_id: int
    address: str
    province_id: int
    district_id: int
    ward_id: int

    @staticmethod
    def parser_dict(data: Dict[str, Any]) -> Sequence[Tuple]:
        result: tuple = (
            data.get(KEY_INPUT_DICT_STORE.NAME.value),
            data.get(KEY_INPUT_DICT_STORE.PHONE.value),
            data.get(KEY_INPUT_DICT_STORE.GROUP_ADDRESS_ID.value),
            data.get(KEY_INPUT_DICT_STORE.CUS_ID.value),
            data.get(KEY_INPUT_DICT_STORE.ADDRESS.value),
            data.get(KEY_INPUT_DICT_STORE.PROVINCE_ID.value),
            data.get(KEY_INPUT_DICT_STORE.DISTRICT_ID.value),
            data.get(KEY_INPUT_DICT_STORE.WARDS_ID.value)
        )
        return result

    @staticmethod
    def parser_class(cls, **kwargs) -> Dict[str, Any]:
        payload: dict = {
            KEY_OUTPUT_DICT_STORE.NAME.value: cls.name,
            KEY_OUTPUT_DICT_STORE.PHONE.value: cls.phone,
            KEY_OUTPUT_DICT_STORE.GROUP_ADDRESS_ID.value: cls.group_address_id,
            KEY_OUTPUT_DICT_STORE.CUS_ID.value: cls.cus_id,
            KEY_OUTPUT_DICT_STORE.ADDRESS.value: cls.address,
            KEY_OUTPUT_DICT_STORE.PROVINCE_ID.value: kwargs.get(KEY_OUTPUT_DICT_STORE.PROVINCE_ID.value),
            KEY_OUTPUT_DICT_STORE.DISTRICT_ID.value: kwargs.get(KEY_OUTPUT_DICT_STORE.DISTRICT_ID.value),
            KEY_OUTPUT_DICT_STORE.WARD_ID.value: kwargs.get(KEY_OUTPUT_DICT_STORE.WARD_ID.value),
        }
        return payload
