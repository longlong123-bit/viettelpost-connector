from typing import List
from odoo import fields, api, models, _
from odoo.exceptions import UserError
from odoo.tools import ustr
from odoo.addons.viettelpost_connector.common.constants import Message
from odoo.addons.viettelpost_connector.dataclass.viettelpost_office import PostOffice
from odoo.addons.viettelpost_connector.common.action import Action


class ViettelPostOffice(models.Model):
    _name = 'viettelpost.office'
    _description = 'List ViettelPost Office'

    name = fields.Char(string='Post office name')
    code = fields.Char(string='Post office code')
    province_name = fields.Char(string='Province name')
    district_name = fields.Char(string='District name')
    ward_name = fields.Char(string='Ward name')
    address = fields.Char(string='Address')
    latitude = fields.Char(string='Latitude')
    longitude = fields.Char(string='Longitude')
    phone = fields.Char(string='Phone')
    person_in_charge = fields.Char(string='Person in charge')
    person_in_charge_phone = fields.Char(string='Person in charge phone')

    @api.model
    def sync_office(self):
        try:
            client = self.env['api.connect.instances'].generate_client_api()
            data_offices: list = []
            result = client.get_offices()
            if result:
                lst_dataclass_office: List[PostOffice] = [PostOffice(*PostOffice.parser_dict(res)) for res in result]
                office_ids = self.search([('code', 'in', [rec.code for rec in lst_dataclass_office])])
                office_codes: List[str] = [res.code for res in office_ids]
                for data in lst_dataclass_office:
                    if data.code not in office_codes:
                        data_offices.append(PostOffice.parser_class(data))
                if data_offices:
                    self.create(data_offices)
            return Action.display_notification(_('Sync post office successfully!'), _(Message.MSG_ACTION_SUCCESS))
        except Exception as e:
            raise UserError(_(f'Sync office failed. Error: {ustr(e)}'))
