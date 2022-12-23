from odoo import fields, api, models, _
from odoo.exceptions import UserError

from odoo.addons.viettelpost_connector.contanst.viettelpost_contanst import Const
from odoo.addons.viettelpost_connector.contanst.viettelpost_contanst import Message


class ViettelPostOffice(models.Model):
    _name = 'viettelpost.office'
    _description = 'List ViettelPost Office'

    name = fields.Char(string='Post office name')
    code = fields.Char(string='Post office code')
    province_name = fields.Char(string='Province name')
    district_name = fields.Char(string='District name')
    ward_name = fields.Char(string='Ward name')
    street = fields.Char(string='Street')
    latitude = fields.Char(string='Latitude')
    longitude = fields.Char(string='Longitude')
    number_phone = fields.Char(string='Phone')
    person_in_charge = fields.Char(string='Person in charge')
    person_in_charge_phone = fields.Char(string='Person in charge phone')
    delivery_carrier_id = fields.Many2one('delivery.carrier', string='Delivery Carrier')

    @api.model
    def sync_office(self):
        client = self.env['api.connect.config'].generate_client_api()
        try:
            data_offices = []
            delivery_carrier_id = self.env['delivery.carrier'].search(
                [('delivery_carrier_code', '=', Const.DELIVERY_CARRIER_CODE)])
            if not delivery_carrier_id:
                raise UserError(_(Message.MSG_NOT_CARRIER))
            dataset = client.get_offices()
            if len(dataset) > 0:
                lst_office_ids = [rec['MA_BUUCUC'] for rec in dataset]
                results = self.search([('code', 'in', lst_office_ids)])
                result_ids = [res.id for res in results]
                dataset = list(filter(lambda x: x['MA_BUUCUC'] not in result_ids, dataset))
                if len(dataset) > 0:
                    for data in dataset:
                        dict_office = {
                            'name': data['TEN_BUUCUC'],
                            'code': data['MA_BUUCUC'],
                            'province_name': data['TEN_TINH'],
                            'district_name': data['TEN_QUANHUYEN'],
                            'ward_name': data['TEN_PHUONGXA'],
                            'street': data['DIA_CHI'],
                            'latitude': data['LATITUDE'],
                            'longitude': data['LONGITUDE'],
                            'number_phone': data['DIEN_THOAI'],
                            'person_in_charge': data['PHUTRACH'],
                            'person_in_charge_phone': data['PHUTRACHPHONE'],
                            'delivery_carrier_id': delivery_carrier_id.id
                        }
                        data_offices.append(dict_office)
            self.create(data_offices)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Sync Post Office Successfully!"),
                    "type": "success",
                    "message": _(Message.MSG_ACTION_SUCCESS),
                    "sticky": False,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
        except Exception as e:
            raise UserError(_(f'Sync office failed. Error: {str(e)}'))
