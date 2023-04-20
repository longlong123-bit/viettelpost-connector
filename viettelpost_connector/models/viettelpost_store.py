from typing import List
from odoo import fields, api, models, _
from odoo.exceptions import UserError

from odoo.addons.viettelpost_connector.common.constants import Message
from odoo.addons.viettelpost_connector.dataclass.viettelpost_store import Store
from odoo.addons.viettelpost_connector.common.action import Action


class ViettelPostStore(models.Model):
    _name = 'viettelpost.store'
    _description = 'List ViettelPost Store'

    name = fields.Char(string='Name', required=True)
    phone = fields.Char(string='Phone', required=True)
    group_address_id = fields.Integer(string='Group Address Id', required=True)
    customer_id = fields.Integer(string='Customer Id', required=True)
    address = fields.Char(string='Address', required=True)
    province_id = fields.Many2one('viettelpost.province', string='Province', required=True)
    district_id = fields.Many2one('viettelpost.district', string='District', required=True)
    ward_id = fields.Many2one('viettelpost.ward', string='Ward', required=True)

    @api.model
    def sync_store(self):
        try:
            client = self.env['api.connect.instances'].generate_client_api()
            data_stores: list = []
            result = client.get_stores()
            if result:
                lst_dataclass_store: List[Store] = [Store(*Store.parser_dict(res)) for res in result]
                grp_address_ids: List[int] = [rec.group_address_id for rec in lst_dataclass_store]
                lst_grp_address_ids = self.search([('group_address_id', 'in', grp_address_ids)])
                grp_address_ids: List[int] = [rec.group_address_id for rec in lst_grp_address_ids]
                for data in lst_dataclass_store:
                    if data.group_address_id not in grp_address_ids:
                        ward_id = self.env['viettelpost.ward'].search([('ward_id', '=', data.ward_id)])
                        district_id = self.env['viettelpost.district'].search([('district_id', '=', data.district_id)])
                        province_id = self.env['viettelpost.province'].search([('province_id', '=', data.province_id)])
                        data_stores.append(Store.parser_class(data, province_id=province_id.id,
                                                              district_id=district_id.id, ward_id=ward_id.id))
                if data_stores:
                    self.create(data_stores)
            return Action.display_notification(_("Sync store successfully!"), _(Message.MSG_ACTION_SUCCESS))
        except Exception as e:
            raise UserError(_(f'Sync Store failed. Error: {str(e)}'))

