from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Sequence, Tuple
from odoo.addons.api_connect_instances.dataclass.dictionary_io import InputDict, OutputDict


class KEY_INPUT_DICT_OFFICE(Enum):
    PROVINCE_NAME: str = 'TEN_TINH'
    DISTRICT_NAME: str = 'TEN_QUANHUYEN'
    WARD_NAME: str = 'TEN_PHUONGXA'
    OFFICE_CODE: str = 'MA_BUUCUC'
    OFFICE_NAME: str = 'TEN_BUUCUC'
    OFFICE_PHONE: str = 'DIEN_THOAI'
    ADDRESS: str = 'DIA_CHI'
    LATITUDE: str = 'LATITUDE'
    LONGITUDE: str = 'LONGITUDE'
    PERSON_IN_CHARGE: str = 'PHUTRACH'
    PERSON_IN_CHARGE_PHONE: str = 'PHUTRACHPHONE'


class KEY_OUTPUT_DICT_OFFICE(Enum):
    OFFICE_NAME: str = 'name'
    OFFICE_CODE: str = 'code'
    PROVINCE_NAME: str = 'province_name'
    DISTRICT_NAME: str = 'district_name'
    WARD_NAME: str = 'ward_name'
    ADDRESS: str = 'address'
    LATITUDE: str = 'latitude'
    LONGITUDE: str = 'longitude'
    OFFICE_PHONE: str = 'phone'
    PERSON_IN_CHARGE: str = 'person_in_charge'
    PERSON_IN_CHARGE_PHONE: str = 'person_in_charge_phone'


@dataclass(frozen=True)
class PostOffice(InputDict, OutputDict):
    name: str
    code: str
    province_name: str
    district_name: str
    ward_name: str
    address: str
    latitude: str
    longitude: str
    phone: str
    person_in_charge: str
    person_in_charge_phone: str

    @staticmethod
    def parser_dict(data: Dict[str, Any]) -> Sequence[Tuple]:
        result: tuple = (
            data.get(KEY_INPUT_DICT_OFFICE.OFFICE_NAME.value),
            data.get(KEY_INPUT_DICT_OFFICE.OFFICE_CODE.value),
            data.get(KEY_INPUT_DICT_OFFICE.PROVINCE_NAME.value),
            data.get(KEY_INPUT_DICT_OFFICE.DISTRICT_NAME.value),
            data.get(KEY_INPUT_DICT_OFFICE.WARD_NAME.value),
            data.get(KEY_INPUT_DICT_OFFICE.ADDRESS.value),
            data.get(KEY_INPUT_DICT_OFFICE.LATITUDE.value),
            data.get(KEY_INPUT_DICT_OFFICE.LONGITUDE.value),
            data.get(KEY_INPUT_DICT_OFFICE.OFFICE_PHONE.value),
            data.get(KEY_INPUT_DICT_OFFICE.PERSON_IN_CHARGE.value),
            data.get(KEY_INPUT_DICT_OFFICE.PERSON_IN_CHARGE_PHONE.value)
        )
        return result

    @staticmethod
    def parser_class(cls, **kwargs) -> Dict[str, Any]:
        payload: dict = {
            KEY_OUTPUT_DICT_OFFICE.OFFICE_NAME.value: cls.name,
            KEY_OUTPUT_DICT_OFFICE.OFFICE_CODE.value: cls.code,
            KEY_OUTPUT_DICT_OFFICE.OFFICE_PHONE.value: cls.phone,
            KEY_OUTPUT_DICT_OFFICE.PROVINCE_NAME.value: cls.province_name,
            KEY_OUTPUT_DICT_OFFICE.DISTRICT_NAME.value: cls.district_name,
            KEY_OUTPUT_DICT_OFFICE.WARD_NAME.value: cls.ward_name,
            KEY_OUTPUT_DICT_OFFICE.LATITUDE.value: cls.latitude,
            KEY_OUTPUT_DICT_OFFICE.LONGITUDE.value: cls.longitude,
            KEY_OUTPUT_DICT_OFFICE.ADDRESS.value: cls.address,
            KEY_OUTPUT_DICT_OFFICE.PERSON_IN_CHARGE.value: cls.person_in_charge,
            KEY_OUTPUT_DICT_OFFICE.PERSON_IN_CHARGE_PHONE.value: cls.person_in_charge_phone
        }
        return payload
