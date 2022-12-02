from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'
    _description = 'Configuration ViettelPost Carrier'

    vtp_store_ids = fields.One2many('viettelpost.store', 'delivery_carrier_id', string='Stores')
    vtp_service_ids = fields.One2many('viettelpost.service', 'delivery_carrier_id', string='Services')
    vtp_post_office_ids = fields.One2many('viettelpost.office', 'delivery_carrier_id', string='Post Offices')
    vtp_province_ids = fields.One2many('vtp.country.province', 'delivery_carrier_id', string='Provinces')
    vtp_district_ids = fields.One2many('vtp.country.district', 'delivery_carrier_id', string='Districts')
    vtp_ward_ids = fields.One2many('vtp.country.ward', 'delivery_carrier_id', string='Wards')
    delivery_carrier_code = fields.Char(string='Delivery Carrier Code')
