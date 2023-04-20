from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Sequence, Tuple, List
from odoo import _
from odoo.exceptions import UserError
from .dictionary_io import InputDict, OutputDict
from odoo.addons.viettelpost_connector.common.constants import Const


class KEY_INPUT_DICT_ORDER(Enum):
    ORDER_NUMBER: str = 'ORDER_NUMBER'
    MONEY_COLLECTION: str = 'MONEY_COLLECTION'
    EXCHANGE_WEIGHT: str = 'EXCHANGE_WEIGHT'
    MONEY_TOTAL: str = 'MONEY_TOTAL'
    MONEY_TOTAL_FEE: str = 'MONEY_TOTAL_FEE'
    MONEY_FEE: str = 'MONEY_FEE'
    MONEY_COLLECTION_FEE: str = 'MONEY_COLLECTION_FEE'
    MONEY_OTHER_FEE: str = 'MONEY_OTHER_FEE'
    MONEY_VAT: str = 'MONEY_VAT'
    KPI_HT: str = 'KPI_HT'


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


class KEY_OUTPUT_DICT_SENDER(Enum):
    GROUP_ADDRESS_ID: str = 'GROUPADDRESS_ID'
    CUS_ID: str = 'CUS_ID'
    SENDER_FULLNAME: str = 'SENDER_FULLNAME'
    SENDER_ADDRESS: str = 'SENDER_ADDRESS'
    SENDER_PHONE: str = 'SENDER_PHONE'
    SENDER_WARD: str = 'SENDER_WARD'
    SENDER_DISTRICT: str = 'SENDER_DISTRICT'
    SENDER_PROVINCE: str = 'SENDER_PROVINCE'
    SENDER_LATITUDE: str = 'SENDER_LATITUDE'
    SENDER_LONGITUDE: str = 'SENDER_LONGITUDE'


class KEY_OUTPUT_DICT_RECEIVER(Enum):
    RECEIVER_FULLNAME: str = 'RECEIVER_FULLNAME'
    RECEIVER_ADDRESS: str = 'RECEIVER_ADDRESS'
    RECEIVER_PHONE: str = 'RECEIVER_PHONE'
    RECEIVER_EMAIL: str = 'RECEIVER_EMAIL'
    RECEIVER_WARD: str = 'RECEIVER_WARD'
    RECEIVER_DISTRICT: str = 'RECEIVER_DISTRICT'
    RECEIVER_PROVINCE: str = 'RECEIVER_PROVINCE'
    RECEIVER_LATITUDE: str = 'RECEIVER_LATITUDE'
    RECEIVER_LONGITUDE: str = 'RECEIVER_LONGITUDE'


class KEY_OUTPUT_DICT_ORDER_INFORMATION(Enum):
    ORDER_NUMBER: str = 'ORDER_NUMBER'
    DELIVERY_DATE: str = 'DELIVERY_DATE'
    PRODUCT_TYPE: str = 'PRODUCT_TYPE'
    NATIONAL_TYPE: str = 'NATIONAL_TYPE'
    ORDER_PAYMENT: str = 'ORDER_PAYMENT'
    ORDER_SERVICE: str = 'ORDER_SERVICE'
    ORDER_SERVICE_ADD: str = 'ORDER_SERVICE_ADD'
    ORDER_NOTE: str = 'ORDER_NOTE'
    MONEY_COLLECTION: str = 'MONEY_COLLECTION'
    MONEY_TOTAL: str = 'MONEY_TOTAL'
    PRODUCT_NAME: str = 'PRODUCT_NAME'
    PRODUCT_DESCRIPTION: str = 'PRODUCT_DESCRIPTION'
    PRODUCT_QUANTITY: str = 'PRODUCT_QUANTITY'
    PRODUCT_PRICE: str = 'PRODUCT_PRICE'
    PRODUCT_WEIGHT: str = 'PRODUCT_WEIGHT'
    LIST_ITEM: str = 'LIST_ITEM'


@dataclass(frozen=True)
class Order(InputDict, OutputDict):
    order_number: str
    money_collection: int
    exchange_weight: int
    money_total: int
    money_total_fee: int
    money_fee: int
    money_collection_fee: int
    money_other_fee: int
    money_vat: int
    kpi_ht: int

    @staticmethod
    def parser_dict(data: Dict[str, Any]) -> Sequence[Tuple]:
        result: tuple = (
            data.get(KEY_INPUT_DICT_ORDER.ORDER_NUMBER.value),
            data.get(KEY_INPUT_DICT_ORDER.MONEY_COLLECTION.value),
            data.get(KEY_INPUT_DICT_ORDER.EXCHANGE_WEIGHT.value),
            data.get(KEY_INPUT_DICT_ORDER.MONEY_TOTAL.value),
            data.get(KEY_INPUT_DICT_ORDER.MONEY_TOTAL_FEE.value),
            data.get(KEY_INPUT_DICT_ORDER.MONEY_FEE.value),
            data.get(KEY_INPUT_DICT_ORDER.MONEY_COLLECTION_FEE.value),
            data.get(KEY_INPUT_DICT_ORDER.MONEY_OTHER_FEE.value),
            data.get(KEY_INPUT_DICT_ORDER.MONEY_VAT.value),
            data.get(KEY_INPUT_DICT_ORDER.KPI_HT.value)
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

    @staticmethod
    def parser_sender(cls) -> Dict[str, Any]:
        payload: dict = {
            KEY_OUTPUT_DICT_SENDER.SENDER_FULLNAME.value: cls.sender_id.name,
            KEY_OUTPUT_DICT_SENDER.SENDER_PHONE.value: cls.sender_id.phone,
            KEY_OUTPUT_DICT_SENDER.SENDER_ADDRESS.value: cls.sender_id.address,
            KEY_OUTPUT_DICT_SENDER.SENDER_WARD.value: cls.sender_id.ward_id.ward_id,
            KEY_OUTPUT_DICT_SENDER.SENDER_DISTRICT.value: cls.sender_id.district_id.district_id,
            KEY_OUTPUT_DICT_SENDER.SENDER_PROVINCE.value: cls.sender_id.province_id.province_id,
            KEY_OUTPUT_DICT_SENDER.GROUP_ADDRESS_ID.value: cls.sender_id.group_address_id,
            KEY_OUTPUT_DICT_SENDER.CUS_ID.value: cls.sender_id.customer_id,
            KEY_OUTPUT_DICT_SENDER.SENDER_LATITUDE.value: 0,
            KEY_OUTPUT_DICT_SENDER.SENDER_LONGITUDE.value: 0
        }
        return payload

    @staticmethod
    def parser_receiver(cls) -> Dict[str, Any]:
        payload: dict = {
            KEY_OUTPUT_DICT_RECEIVER.RECEIVER_FULLNAME.value: cls.receiver_id.name,
            KEY_OUTPUT_DICT_RECEIVER.RECEIVER_PHONE.value: cls.receiver_id.phone,
            KEY_OUTPUT_DICT_RECEIVER.RECEIVER_ADDRESS.value: cls.receiver_id.vtp_street,
            KEY_OUTPUT_DICT_RECEIVER.RECEIVER_EMAIL.value: cls.receiver_id.email,
            KEY_OUTPUT_DICT_RECEIVER.RECEIVER_WARD.value: cls.receiver_id.vtp_ward_id.ward_id,
            KEY_OUTPUT_DICT_RECEIVER.RECEIVER_DISTRICT.value: cls.receiver_id.vtp_district_id.district_id,
            KEY_OUTPUT_DICT_RECEIVER.RECEIVER_PROVINCE.value: cls.receiver_id.vtp_province_id.province_id,
            KEY_OUTPUT_DICT_RECEIVER.RECEIVER_LATITUDE.value: 0,
            KEY_OUTPUT_DICT_RECEIVER.RECEIVER_LONGITUDE.value: 0
        }
        return payload

    @staticmethod
    def _prepare_data_order_line(cls):
        list_item: list = []
        total_weight: float = 0.0
        total_qty: float = 0.0
        total_price: float = 0.0
        if cls.deli_order_id.sale_id.order_line:
            for line in cls.deli_order_id.sale_id.order_line:
                gross_width: float = line.product_id.product_tmpl_id.gross_width
                gross_height: float = line.product_id.product_tmpl_id.gross_height
                gross_depth: float = line.product_id.product_tmpl_id.gross_depth
                weight: float = (gross_width * gross_height * gross_depth) / 6000.0
                order_line: dict = {
                    KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_NAME.value: line.product_id.product_tmpl_id.name,
                    KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_PRICE.value: line.price_subtotal,
                    KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_WEIGHT.value: weight,
                    KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_QUANTITY.value: line.product_uom_qty
                }
                total_price += line.price_subtotal
                total_weight += weight
                total_qty += line.product_uom_qty
                list_item.append(order_line)
            return list_item, total_weight, total_qty, total_price
        else:
            raise UserError(_('Please add products to order line.'))

    @staticmethod
    def _prepare_payload_check_ship_code(cls) -> Dict[str, Any]:
        list_item, total_weight, total_qty, total_price = Order._prepare_data_order_line(cls)
        payload: dict = {
            KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_WEIGHT.value: total_weight,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_PRICE.value: total_price,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.MONEY_COLLECTION.value: 0,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.ORDER_SERVICE_ADD.value: cls.service_extend_id.extend_code or '',
            KEY_OUTPUT_DICT_ORDER_INFORMATION.ORDER_SERVICE.value: cls.service_id.code,
            KEY_OUTPUT_DICT_SENDER.SENDER_PROVINCE.value: cls.sender_id.province_id.province_id,
            KEY_OUTPUT_DICT_SENDER.SENDER_DISTRICT.value: cls.sender_id.district_id.district_id,
            KEY_OUTPUT_DICT_RECEIVER.RECEIVER_PROVINCE.value: cls.receiver_id.province_id.province_id,
            KEY_OUTPUT_DICT_RECEIVER.RECEIVER_DISTRICT.value: cls.receiver_id.district_id.district_id,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_TYPE.value: cls.product_type_id.code,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.NATIONAL_TYPE.value: int(cls.national_type_id.code)
        }
        return payload

    @staticmethod
    def _compute_money_collection(cls) -> Sequence[float]:
        collection: float = 0.0
        fee: float = 0.0
        list_item, total_weight, total_qty, total_price = Order._prepare_data_order_line(cls)
        if cls.waybill_type_id.code in [Const.WAYBILL_TYPE_CODE_2, Const.WAYBILL_TYPE_CODE_4]:
            client = cls.env['api.connect.instances'].generate_client_api()
            payload = Order._prepare_payload_check_ship_code(cls)
            res = client.check_ship_cost(payload)
            if cls.waybill_type_id.code == Const.WAYBILL_TYPE_CODE_2:
                collection = total_price
                fee = res.get('MONEY_TOTAL', 0)
            elif cls.waybill_type_id.code == Const.WAYBILL_TYPE_CODE_4:
                collection = res.get('MONEY_TOTAL', 0)
        elif cls.waybill_type_id.code == Const.WAYBILL_TYPE_CODE_3:
            collection = float(cls.deli_order_id.sale_id.amount_untaxed)
        return collection, fee

    @staticmethod
    def parser_order(cls) -> Dict[str, Any]:
        list_item, total_weight, total_qty, total_price = Order._prepare_data_order_line(cls)
        money_collection, money_total = Order._compute_money_collection(cls)
        payload: dict = {
            KEY_OUTPUT_DICT_ORDER_INFORMATION.ORDER_NUMBER.value: cls.deli_order_id.sale_id.name,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.DELIVERY_DATE.value: datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_TYPE.value: cls.product_type_id.code,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.ORDER_PAYMENT.value: int(cls.waybill_type_id.code),
            KEY_OUTPUT_DICT_ORDER_INFORMATION.ORDER_SERVICE.value: cls.service_id.code,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.ORDER_SERVICE_ADD.value: cls.service_extend_id.extend_code or '',
            KEY_OUTPUT_DICT_ORDER_INFORMATION.MONEY_COLLECTION.value: money_collection,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.MONEY_TOTAL.value: money_total,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_NAME.value: cls.deli_order_id.sale_id.order_line[0].product_id.product_tmpl_id.name,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_DESCRIPTION.value: cls.deli_order_id.sale_id.order_line[0].product_id.product_tmpl_id.name,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_QUANTITY.value: total_qty,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_PRICE.value: total_price,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_WEIGHT.value: total_weight,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.ORDER_NOTE.value: cls.note or '',
            KEY_OUTPUT_DICT_ORDER_INFORMATION.LIST_ITEM.value: 0
        }
        return payload
