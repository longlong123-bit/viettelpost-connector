from odoo import fields, models


class WaybillType(models.Model):
    _name = 'viettelpost.waybill.type'
    _description = 'ViettelPost Waybill Type'

    name = fields.Char(string='Name', required=True, readonly=True)
    code = fields.Char(string='Code', required=True, readonly=True)