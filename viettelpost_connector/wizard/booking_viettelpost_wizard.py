from odoo import models, fields, _, api
from odoo.tools import ustr
from odoo.exceptions import ValidationError, UserError
from odoo.addons.viettelpost_connector.common.constants import Const
from odoo.addons.viettelpost_connector.dataclass.viettelpost_order import Order


class BookingViettelpostWizard(models.TransientModel):
    _name = 'booking.viettelpost.wizard'
    _description = 'This module fills and confirms info about shipment before creating a bill of lading Viettelpost.'

    def _default_product_type(self) -> models:
        product_type_id = self.env.ref('viettelpost_connector.viettelpost_product_type_2')
        if product_type_id:
            return product_type_id.id

    def _default_national_type(self) -> models:
        national_type_id = self.env.ref('viettelpost_connector.viettelpost_national_type_1')
        if national_type_id:
            return national_type_id.id

    def _default_waybill_type(self) -> models:
        waybill_type_id = self.env.ref('viettelpost_connector.viettelpost_waybill_type_1')
        if waybill_type_id:
            return waybill_type_id.id

    def _default_service_type(self) -> models:
        service_id = self.env['viettelpost.service'].search([('code', '=', Const.SERVICE_TYPE)])
        if service_id:
            return service_id

    carrier_id = fields.Many2one('delivery.carrier', string='Delivery Carrier', required=True, readonly=True)
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

    @api.onchange('service_id')
    def _onchange_service_id(self):
        for rec in self:
            if rec.service_id:
                return {
                    'domain':
                        {
                            'service_extend_id': [('service_id', '=', rec.service_id.id)]
                        }
                }

    def _prepare_data_create_line_amount_ship_fee(self, dataclass: Order):
        payload: dict = {
            'product_id': self.carrier_id.product_id.id,
            'name': f'{self.service_id.display_name}\n{self.service_extend_id.display_name}'
            if self.service_extend_id else f'{self.service_id.display_name}',
            'product_uom_qty': 1.0,
            'price_unit': dataclass.money_total,
            'price_subtotal': dataclass.money_total,
            'price_total': dataclass.money_total,
            'sequence': self.deli_order_id.sale_id.order_line[-1].sequence + 1,
            'order_id': self.deli_order_id.sale_id.order_line[-1].order_id.id,
            'is_delivery': True
        }
        return payload

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
            result = client.create_waybill(payload)
            dataclass_order = Order(*Order.parser_dict(result))
            payload_do = Order.parser_class(dataclass_order, carrier_id=self.carrier_id.id)
            self.deli_order_id.write(payload_do)
            line_data_ship_fee = self._prepare_data_create_line_amount_ship_fee(dataclass_order)
            self.env['sale.order.line'].create(line_data_ship_fee)
        except Exception as e:
            raise UserError(_(ustr(e)))
