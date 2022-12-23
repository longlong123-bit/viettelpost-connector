from odoo import fields, api, models, _
from odoo.exceptions import UserError

from odoo.addons.viettelpost_connector.contanst.viettelpost_contanst import Const
from odoo.addons.viettelpost_connector.contanst.viettelpost_contanst import Message


class ViettelPostStore(models.Model):
    _name = 'viettelpost.store'
    _description = 'List ViettelPost Store'

    name = fields.Char(string='Name', required=1)
    phone = fields.Char(string='Phone', required=1)
    email = fields.Char(string='Email')
    group_address_id = fields.Integer(string='Group Address Id', required=1)
    customer_id = fields.Integer(string='Customer Id', required=1)
    address = fields.Char(string='Address', required=1)
    province_id = fields.Many2one('vtp.country.province', string='Province', required=1)
    district_id = fields.Many2one('vtp.country.district', string='District', required=1)
    ward_id = fields.Many2one('vtp.country.ward', string='Ward', required=1)
    delivery_carrier_id = fields.Many2one('delivery.carrier', string='Delivery Carrier')

    @api.model
    def sync_store(self):
        client = self.env['api.connect.config'].generate_client_api()
        try:
            data_stores = []
            delivery_carrier_id = self.env['delivery.carrier'].search(
                [('delivery_carrier_code', '=', Const.DELIVERY_CARRIER_CODE)])
            if not delivery_carrier_id:
                raise UserError(_(Message.MSG_NOT_CARRIER))
            dataset = client.get_stores()
            if len(dataset) > 0:
                for data in dataset:
                    store_id = self.search([('group_address_id', '=', data['groupaddressId'])])
                    province_id = self.env['vtp.country.province'].search([('province_id', '=', data['provinceId'])])
                    district_id = self.env['vtp.country.district'].search([('district_id', '=', data['districtId'])])
                    ward_id = self.env['vtp.country.ward'].search([('ward_id', '=', data['wardsId'])])
                    if not store_id:
                        dict_store = {
                            'name': data['name'],
                            'phone': data['phone'],
                            'group_address_id': int(data['groupaddressId']),
                            'customer_id': int(data['cusId']),
                            'address': data['address'],
                            'province_id': province_id.id,
                            'district_id': district_id.id,
                            'ward_id': ward_id.id,
                            'delivery_carrier_id': delivery_carrier_id.id
                        }
                        data_stores.append(dict_store)
            self.create(data_stores)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Sync Store Successfully!"),
                    "type": "success",
                    "message": _(Message.MSG_ACTION_SUCCESS),
                    "sticky": False,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
        except Exception as e:
            raise UserError(_(f'Sync Store failed. Error: {str(e)}'))

