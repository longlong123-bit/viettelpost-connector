from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'
    _description = 'Configuration ViettelPost Carrier'

    delivery_type = fields.Selection(selection_add=[('viettelpost', 'Viettelpost')])
