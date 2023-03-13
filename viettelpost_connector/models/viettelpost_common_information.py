from odoo import fields, models


class NationalType(models.Model):
    _name = 'viettelpost.national.type'
    _description = 'ViettelPost National Type'

    name = fields.Char(string='Name', required=True, readonly=True)
    code = fields.Char(string='Code', required=True, readonly=True)


class WaybillType(models.Model):
    _name = 'viettelpost.waybill.type'
    _description = 'ViettelPost Waybill Type'

    name = fields.Char(string='Name', required=True, readonly=True)
    code = fields.Char(string='Code', required=True, readonly=True)


class Status(models.Model):
    _name = 'viettelpost.status'
    _description = 'ViettelPost Status'
    _order = 'code asc'

    name = fields.Char(string='Name', required=True, readonly=True)
    code = fields.Char(string='Code', required=True, readonly=True)
    description = fields.Char(string='Description', required=True, readonly=True)


class ProductType(models.Model):
    _name = 'viettelpost.product.type'
    _description = 'ViettelPost Product Type'

    name = fields.Char(string='Name', required=True, readonly=True)
    code = fields.Char(string='Code', required=True, readonly=True)