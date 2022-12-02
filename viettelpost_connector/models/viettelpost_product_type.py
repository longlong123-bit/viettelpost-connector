from odoo import fields, models


class ProductType(models.Model):
    _name = 'viettelpost.product.type'
    _description = 'ViettelPost Product Type'

    name = fields.Char(string='Name', required=True, readonly=True)
    code = fields.Char(string='Code', required=True, readonly=True)
