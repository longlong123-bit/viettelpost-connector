from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Customize Attributes'

    gross_depth = fields.Float(string='Depth')
    gross_weight = fields.Float(string='Weight')
    gross_width = fields.Float(string='Width')
    gross_height = fields.Float(string='Height')

    def _get_default_millimeter_uom(self):
        return self._get_length_uom_name()

    def _get_default_gram_uom(self):
        return self._get_weight_uom_name()

    millimeter_uom_name = fields.Char(string='Millimeter unit of measure label', compute='_compute_mm_uom_name',
                                      default=_get_default_millimeter_uom)
    gram_uom_name = fields.Char(string='Gram unit of measure label', compute='_compute_gram_uom_name',
                                default=_get_default_gram_uom)

    @api.model
    def _get_length_uom_name(self):
        return self.env.ref('viettelpost_connector.product_uom_millimeter').display_name

    def _compute_mm_uom_name(self):
        for rec in self:
            rec.millimeter_uom_name = self._get_length_uom_name()

    @api.model
    def _get_weight_uom_name(self):
        return self.env.ref('uom.product_uom_gram').display_name

    def _compute_gram_uom_name(self):
        for rec in self:
            rec.gram_uom_name = self._get_weight_uom_name()
