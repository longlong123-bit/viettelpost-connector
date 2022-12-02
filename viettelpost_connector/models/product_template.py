from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Customize Attributes'

    gross_depth = fields.Float(string='Depth (mm)')
    gross_weight = fields.Float(string='Weight (g)')
    gross_width = fields.Float(string='Width (mm)')
    gross_height = fields.Float(string='Height (mm)')

