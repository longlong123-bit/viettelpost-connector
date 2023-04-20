from odoo import models, fields, _
from odoo.tools import ustr
from odoo.exceptions import ValidationError, UserError
from odoo.addons.viettelpost_connector.common.constants import Const
from odoo.addons.viettelpost_connector.dataclass.viettelpost_order import Order


class BookingViettelpostWizard(models.TransientModel):
    _name = 'booking.viettelpost.wizard'
    _description = 'This module fills and confirms info about shipment before creating a bill of lading Viettelpost.'

    def _default_product_type(self) -> models:
        product_type_id = self.env['viettelpost.product.type'].search([('code', '=', Const.PRODUCT_TYPE_CODE_HH)])
        if product_type_id:
            return product_type_id

    def _default_national_type(self) -> models:
        national_type_id = self.env['viettelpost.national.type'].search([('code', '=', Const.NATIONAL_TYPE_CODE)])
        if national_type_id:
            return national_type_id

    def _default_waybill_type(self) -> models:
        waybill_type_id = self.env['viettelpost.waybill.type'].search([('code', '=', Const.WAYBILL_TYPE_CODE_1)])
        if waybill_type_id:
            return waybill_type_id

    def _default_service_type(self) -> models:
        service_id = self.env['viettelpost.service'].search([('code', '=', 'LCOD')])
        if service_id:
            return service_id

    deli_carrier_id = fields.Many2one('delivery.carrier', string='Delivery Carrier', required=True, readonly=True)
    deli_order_id = fields.Many2one('stock.picking', string='Delivery order', required=True, readonly=True)
    service_id = fields.Many2one('viettelpost.service', string='Service', default=_default_service_type, required=True)
    service_extend_id = fields.Many2one('viettelpost.extend.service', string='Service Extend')
    waybill_type_id = fields.Many2one('viettelpost.waybill.type', string='Waybill type',
                                      default=_default_waybill_type, required=True)
    product_type_id = fields.Many2one('viettelpost.product.type', string='Product type',
                                      default=_default_product_type, required=True)
    national_type_id = fields.Many2one('viettelpost.national.type', string='National type',
                                       default=_default_national_type, required=True)
    receiver_id = fields.Many2one('res.partner', string='Receiver', required=True)
    receiver_phone = fields.Char(related='receiver_id.phone', string='Phone')
    receiver_street = fields.Char(related='receiver_id.vtp_street', string='Street')
    receiver_ward_id = fields.Many2one(related='receiver_id.vtp_ward_id', string='Ward')
    receiver_district_id = fields.Many2one(related='receiver_id.vtp_district_id', string='District')
    receiver_province_id = fields.Many2one(related='receiver_id.vtp_province_id', string='Province')

    sender_id = fields.Many2one('viettelpost.store', string='Store', required=True)
    sender_name = fields.Char(related='sender_id.name', string='Sender')
    sender_phone = fields.Char(related='sender_id.phone')
    sender_address = fields.Char(related='sender_id.address', string='Address')
    sender_province_id = fields.Many2one(related='sender_id.province_id', string='Province')
    sender_district_id = fields.Many2one(related='sender_id.district_id', string='District')
    sender_ward_id = fields.Many2one(related='sender_id.ward_id', string='Ward')

    check_unique = fields.Boolean(string='Check unique', help='Check unique to check SO exists in Viettelpost.')
    note = fields.Text(string='Note')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    # def _validate_payload(self):
    #     fields = {
    #         'Delivery carrier': self.deli_carrier_id,
    #         'Delivery order': self.deli_order_id,
    #         'Sender': self.sender_id,
    #         'Sender Phone': self.sender_phone,
    #         'Sender Street': self.sender_street,
    #         'Sender Ward': self.sender_ward_id,
    #         'Sender District': self.sender_district_id,
    #         'Sender Province': self.sender_province_id,
    #         'Store': self.store_id,
    #         'Service Type': self.service_type,
    #         'Order Payment': self.order_payment,
    #         'Product Type': self.product_type,
    #         'National Type': self.national_type,
    #         'Product Name': self.product_name,
    #         'Number of Package': self.no_of_package,
    #         'Receiver': self.receiver_id,
    #         'Receiver Phone': self.receiver_phone,
    #         'Receiver Street': self.receiver_street,
    #         'Receiver Ward': self.receiver_ward_id,
    #         'Receiver District': self.receiver_district_id,
    #         'Receiver Province': self.receiver_province_id,
    #         'List Item': len(self.deli_order_id.sale_id.order_line)
    #     }
    #     for field, value in fields.items():
    #         if not value:
    #             raise ValidationError(_(f'The field {field} is required.'))

    # def _prepare_data_create_line_amount_ship_fee(self, dataclass: ViettelpostDataclass):
    #     service_name = [item[1] for item in BookingViettelpostWizard.get_viettelpost_service_types() if item[0] == self.service_type]
    #     payload: dict = {
    #         'product_id': self.deli_carrier_id.product_id.id,
    #         'name': f'[{self.service_type}] - {service_name[0]}',
    #         'product_uom_qty': 1.0,
    #         'price_unit': dataclass.money_total,
    #         'price_subtotal': dataclass.money_total,
    #         'price_total': dataclass.money_total,
    #         'sequence': self.deli_order_id.sale_id.order_line[-1].sequence + 1,
    #         'order_id': self.deli_order_id.sale_id.order_line[-1].order_id.id,
    #         'is_delivery': True
    #     }
    #     return payload

    def action_booking_viettelpost(self):
        try:
            # self._validate_payload()
            client = self.env['api.connect.instances'].generate_client_api()
            payload = {
                **Order.parser_sender(self),
                **Order.parser_receiver(self),
                **Order.parser_order(self)
            }
            if self.check_unique:
                payload = {**payload, **{'CHECK_UNIQUE': True}}
            result = client.create_order(payload)
            dataclass_vtp = Order(*Order.parser_dict(result))
            # line_data_ship_fee = self._prepare_data_create_line_amount_ship_fee(dataclass_vtp)
            # self.env['sale.order.line'].create(line_data_ship_fee)
        except Exception as e:
            raise UserError(_(ustr(e)))