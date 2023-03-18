from odoo import fields, models, _, api
from odoo.exceptions import UserError
from odoo.addons.viettelpost_connector.common.constants import Const
from odoo.addons.viettelpost_connector.common.constants import Message


class VTPProvince(models.Model):
    _name = 'viettelpost.province'
    _rec_name = 'province_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'ViettelPost Province'

    def _default_country(self):
        return self.env['res.country'].search([('code', '=', 'VN')]).id

    delivery_carrier_id = fields.Many2one('delivery.carrier', string='Delivery Carrier')
    country_id = fields.Many2one('res.country', string='Country', required=True, tracking=True,
                                 default=_default_country)
    province_id = fields.Integer(string='Province ID', required=True, tracking=True)
    province_code = fields.Char(string='Province Code', required=True, tracking=True)
    province_name = fields.Char(string='Province Name', required=True, tracking=True)
    district_ids = fields.One2many('viettelpost.district', 'province_id', string='District')
    vtp_aliases = fields.Text(string='Aliases')

    @api.model
    def sync_province(self):
        try:
            client = self.env['api.connect.config'].generate_client_api()
            data_provinces: list = []
            delivery_carrier_id = self.env['delivery.carrier'].search(
                [('delivery_carrier_code', '=', Const.DELIVERY_CARRIER_CODE)])
            if not delivery_carrier_id:
                raise UserError(_(Message.MSG_NOT_CARRIER))
            dataset = client.get_provinces()
            if len(dataset) > 0:
                lst_province_ids: list = [rec.get('PROVINCE_ID') for rec in dataset]
                results = self.search([('province_id', 'in', lst_province_ids)])
                result_ids: list = [res.province_id for res in results]
                dataset = list(filter(lambda x: x.get('PROVINCE_ID') not in result_ids, dataset))
                if len(dataset) > 0:
                    for data in dataset:
                        data_province: dict = {
                            'province_id': data.get('PROVINCE_ID'),
                            'province_code': data.get('PROVINCE_CODE'),
                            'province_name': data.get('PROVINCE_NAME').title(),
                            'delivery_carrier_id': delivery_carrier_id.id
                        }
                        data_provinces.append(data_province)
                    self.create(data_provinces)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Sync provinces successfully!"),
                    "type": "success",
                    "message": _(Message.MSG_ACTION_SUCCESS),
                    "sticky": False,
                    "next": {"type": "ir.actions.act_window_close"},
                }
            }
        except Exception as e:
            raise UserError(_(f'Sync province failed. Error: {str(e)}'))


class VTPDistrict(models.Model):
    _name = 'viettelpost.district'
    _rec_name = 'district_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'ViettelPost District'

    delivery_carrier_id = fields.Many2one('delivery.carrier', string='Delivery Carrier')
    district_id = fields.Integer(string='District ID', required=True, tracking=True)
    district_code = fields.Char(string='District Code', required=True, tracking=True)
    district_name = fields.Char(string='District Name', required=True, tracking=True)
    province_id = fields.Many2one('viettelpost.province', string='Province', required=True, tracking=True)
    ward_ids = fields.One2many('viettelpost.ward', 'district_id', string='Ward')
    vtp_aliases = fields.Text(string='Aliases')

    @api.model
    def sync_district(self):
        data_districts: list = []
        try:
            client = self.env['api.connect.config'].generate_client_api()
            delivery_carrier_id = self.env['delivery.carrier'].search(
                [('delivery_carrier_code', '=', Const.DELIVERY_CARRIER_CODE)])
            if not delivery_carrier_id:
                raise UserError(_(Message.MSG_NOT_CARRIER))
            dataset = client.get_districts()
            if len(dataset) > 0:
                lst_district_ids: list = [rec.get('DISTRICT_ID') for rec in dataset]
                results = self.search([('district_id', 'in', lst_district_ids)])
                result_ids: list = [res.district_id for res in results]
                dataset = list(filter(lambda x: x.get('DISTRICT_ID') not in result_ids, dataset))
                if len(dataset) > 0:
                    for data in dataset:
                        province_id = self.env['viettelpost.province'].search([('province_id', '=', data.get('PROVINCE_ID'))])
                        if not province_id:
                            continue
                        data_district: dict = {
                            'district_id': data.get('DISTRICT_ID'),
                            'district_code': data.get('DISTRICT_VALUE'),
                            'district_name': data.get('DISTRICT_NAME').title(),
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


class VTPWard(models.Model):
    _name = 'viettelpost.ward'
    _rec_name = 'ward_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'ViettelPost Ward'

    delivery_carrier_id = fields.Many2one('delivery.carrier', string='Delivery Carrier')
    ward_id = fields.Integer(string='Ward ID', required=True, tracking=True)
    ward_name = fields.Char(string='Ward Name', required=True, tracking=True)
    district_id = fields.Many2one('viettelpost.district', string='District', required=True, tracking=True)
    vtp_aliases = fields.Text(string='Aliases')

    @api.model
    def sync_ward(self):
        try:
            client = self.env['api.connect.config'].generate_client_api()
            data_wards: list = []
            delivery_carrier_id = self.env['delivery.carrier'].search(
                [('delivery_carrier_code', '=', Const.DELIVERY_CARRIER_CODE)])
            if not delivery_carrier_id:
                raise UserError(_(Message.MSG_NOT_CARRIER))
            dataset = client.get_wards()
            if len(dataset) > 0:
                lst_ward_ids: list = [rec.get('WARDS_ID') for rec in dataset]
                results = self.search([('ward_id', 'in', lst_ward_ids)])
                result_ids: list = [res.ward_id for res in results]
                dataset = list(filter(lambda x: x['WARDS_ID'] not in result_ids, dataset))
                if len(dataset) > 0:
                    for data in dataset:
                        district_id = self.env['viettelpost.district'].search([('district_id', '=', data.get('DISTRICT_ID'))])
                        if not district_id:
                            continue
                        data_ward: dict = {
                            'ward_id': data.get('WARDS_ID'),
                            'ward_name': data.get('WARDS_NAME').title(),
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
