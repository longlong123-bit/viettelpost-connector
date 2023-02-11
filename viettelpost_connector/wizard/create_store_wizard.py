from odoo import fields, models, _, api
from odoo.exceptions import UserError
from odoo.addons.viettelpost_connector.common.constants import Const
from odoo.addons.viettelpost_connector.common.constants import Message


class CreateStoreWizard(models.Model):
    _name = 'create.store.wizard'
    _description = 'Form Create Store To ViettelPost'

    name = fields.Char(string='Name', required=True)
    phone = fields.Char(string='Phone', required=True)
    address = fields.Char(string='Address', required=True)
    ward_id = fields.Many2one('vtp.country.ward', string='Ward', required=True)

    @api.model
    def create_store(self):
        action = self.env.ref('viettelpost_connector.create_store_wizard_wizard_action').read()[0]
        return action

    def vtp_create_store(self):
        client = self.env['api.connect.config'].generate_client_api()
        try:
            data_offices: list = []
            payload: dict = {
                'NAME': self.name,
                'PHONE': self.phone,
                'ADDRESS': self.address,
                'WARDS_ID': self.ward_id.ward_id
            }
            dataset = client.set_store(payload)
            for data in dataset:
                store_id = self.env['viettelpost.store'].search([('group_address_id', '=', data['groupaddressId'])])
                province_id = self.env['vtp.country.province'].search([('province_id', '=', data['provinceId'])])
                district_id = self.env['vtp.country.district'].search([('district_id', '=', data['districtId'])])
                ward_id = self.env['vtp.country.ward'].search([('ward_id', '=', data['wardsId'])])
                if not store_id:
                    dict_store: dict = {
                        'name': data['name'],
                        'phone': data['phone'],
                        'group_address_id': data['groupaddressId'],
                        'customer_id': data['cusId'],
                        'address': data['address'],
                        'province_id': province_id.id,
                        'district_id': district_id.id,
                        'ward_id': ward_id.id
                    }
                    data_offices.append(dict_store)
            self.create(data_offices)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Create Store Successfully!"),
                    "type": "success",
                    "message": _(Message.MSG_ACTION_SUCCESS),
                    "sticky": False,
                    "next": {"type": "ir.actions.client", "tag": "reload"},
                },
            }
        except Exception as e:
            raise UserError(_(f'Create store failed. Error: {e}'))
