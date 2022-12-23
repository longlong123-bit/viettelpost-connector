from odoo import fields, models, _, api
from odoo.exceptions import UserError

from odoo.addons.viettelpost_connector.contanst.viettelpost_contanst import Const
from odoo.addons.viettelpost_connector.contanst.viettelpost_contanst import Message


class VTPCountryProvince(models.Model):
    _name = 'vtp.country.province'
    _rec_name = 'province_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'ViettelPost Country Province'

    def _default_country(self):
        return self.env['res.country'].search([('code', '=', 'VN')]).id

    delivery_carrier_id = fields.Many2one('delivery.carrier', string='Delivery Carrier')
    country_id = fields.Many2one('res.country', string='Country', required=True, tracking=True, default=_default_country)
    province_id = fields.Integer(string='Province ID', required=True, tracking=True)
    province_code = fields.Char(string='Province Code', required=True, tracking=True)
    province_name = fields.Char(string='Province Name', required=True, tracking=True)
    district_ids = fields.One2many('vtp.country.district', 'province_id', string='District')

    @api.model
    def sync_province(self):
        client = self.env['api.connect.config'].generate_client_api()
        try:
            data_provinces = []
            delivery_carrier_id = self.env['delivery.carrier'].search(
                [('delivery_carrier_code', '=', Const.DELIVERY_CARRIER_CODE)])
            if not delivery_carrier_id:
                raise UserError(_(Message.MSG_NOT_CARRIER))
            dataset = client.get_provinces()
            if len(dataset) > 0:
                lst_province_ids = [rec['PROVINCE_ID'] for rec in dataset]
                results = self.search([('province_id', 'in', lst_province_ids)])
                result_ids = [res.id for res in results]
                dataset = list(filter(lambda x: x['PROVINCE_ID'] not in result_ids, dataset))
                if len(dataset) > 0:
                    for data in dataset:
                        data_province = {
                            'province_id': data['PROVINCE_ID'],
                            'province_code': data['PROVINCE_CODE'],
                            'province_name': data['PROVINCE_NAME'].title(),
                            'delivery_carrier_id': delivery_carrier_id.id
                        }
                        data_provinces.append(data_province)
            self.create(data_provinces)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Sync Provinces Successfully!"),
                    "type": "success",
                    "message": _(Message.MSG_ACTION_SUCCESS),
                    "sticky": False,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
        except Exception as e:
            raise UserError(_(f'Sync province failed. Error: {str(e)}'))


class VTPCountryDistrict(models.Model):
    _name = 'vtp.country.district'
    _rec_name = 'district_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'ViettelPost Country District'

    delivery_carrier_id = fields.Many2one('delivery.carrier', string='Delivery Carrier')
    district_id = fields.Integer(string='District ID', required=True, tracking=True)
    district_code = fields.Char(string='District Code', required=True, tracking=True)
    district_name = fields.Char(string='District Name', required=True, tracking=True)
    province_id = fields.Many2one('vtp.country.province', string='Province', required=True, tracking=True)
    ward_ids = fields.One2many('vtp.country.ward', 'district_id', string='Ward')

    @api.model
    def sync_district(self):
        data_districts = []
        client = self.env['api.connect.config'].generate_client_api()
        try:
            delivery_carrier_id = self.env['delivery.carrier'].search(
                [('delivery_carrier_code', '=', Const.DELIVERY_CARRIER_CODE)])
            if not delivery_carrier_id:
                raise UserError(_(Message.MSG_NOT_CARRIER))
            dataset = client.get_districts()
            if len(dataset) > 0:
                lst_district_ids = [rec['DISTRICT_ID'] for rec in dataset]
                results = self.search([('district_id', 'in', lst_district_ids)])
                result_ids = [res.id for res in results]
                dataset = list(filter(lambda x: x['DISTRICT_ID'] not in result_ids, dataset))
                if len(dataset) > 0:
                    for data in dataset:
                        province_id = self.env['vtp.country.province'].search(
                            [('province_id', '=', data['PROVINCE_ID'])])
                        if not province_id:
                            continue
                        data_district = {
                            'district_id': data['DISTRICT_ID'],
                            'district_code': data['DISTRICT_VALUE'],
                            'district_name': data['DISTRICT_NAME'].title(),
                            'province_id': province_id.id,
                            'delivery_carrier_id': delivery_carrier_id.id
                        }
                        data_districts.append(data_district)
            self.create(data_districts)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Sync District Successfully!"),
                    "type": "success",
                    "message": _(Message.MSG_ACTION_SUCCESS),
                    "sticky": False,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
        except Exception as e:
            raise UserError(_(f'Sync district failed. Error: {str(e)}'))


class VTPCountryWard(models.Model):
    _name = 'vtp.country.ward'
    _rec_name = 'ward_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'ViettelPost Country Ward'

    delivery_carrier_id = fields.Many2one('delivery.carrier', string='Delivery Carrier')
    ward_id = fields.Integer(string='Ward ID', required=True, tracking=True)
    ward_name = fields.Char(string='Ward Name', required=True, tracking=True)
    district_id = fields.Many2one('vtp.country.district', string='District', required=True, tracking=True)

    @api.model
    def sync_ward(self):
        client = self.env['api.connect.config'].generate_client_api()
        try:
            data_wards = []
            delivery_carrier_id = self.env['delivery.carrier'].search(
                [('delivery_carrier_code', '=', Const.DELIVERY_CARRIER_CODE)])
            if not delivery_carrier_id:
                raise UserError(_(Message.MSG_NOT_CARRIER))
            dataset = client.get_wards()
            if len(dataset) > 0:
                lst_ward_ids = [rec['WARDS_ID'] for rec in dataset]
                results = self.search([('ward_id', 'in', lst_ward_ids)])
                result_ids = [res.id for res in results]
                dataset = list(filter(lambda x: x['WARDS_ID'] not in result_ids, dataset))
                if len(dataset) > 0:
                    for data in dataset:
                        district_id = self.env['vtp.country.district'].search(
                            [('district_id', '=', data['DISTRICT_ID'])])
                        if not district_id:
                            continue
                        data_ward = {
                            'ward_id': data['WARDS_ID'],
                            'ward_name': data['WARDS_NAME'].title(),
                            'district_id': district_id.id,
                            'delivery_carrier_id': delivery_carrier_id.id
                        }
                        data_wards.append(data_ward)
            self.create(data_wards)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Sync District Successfully!"),
                    "type": "success",
                    "message": _(Message.MSG_ACTION_SUCCESS),
                    "sticky": False,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
        except Exception as e:
            raise UserError(_(f'Sync ward failed. Error: {str(e)}'))