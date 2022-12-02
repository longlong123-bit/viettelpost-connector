from odoo import fields, models


class NationalType(models.Model):
    _name = 'viettelpost.national.type'
    _description = 'ViettelPost National Type'

    name = fields.Char(string='Name', required=True, readonly=True)
    code = fields.Char(string='Code', required=True, readonly=True)
