from odoo import models, _


class SelectDeliCarrierWizard(models.TransientModel):
    _inherit = 'select.delivery.carrier.wizard'
    _description = 'This module is used open a popup to select delivery carrier'

    def action_assign_delivery(self):
        if self.carrier_id.delivery_type == 'viettelpost':
            return {
                'name': _('Viettelpost Shipment Information'),
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('viettelpost_connector.booking_viettelpost_wizard_form_view').id,
                'res_model': 'booking.viettelpost.wizard',
                'context': {
                    'default_deli_order_id': self.deli_order_id.id,
                    'default_carrier_id': self.carrier_id.id,
                    'default_receiver_id': self.deli_order_id.partner_id.id
                },
                'type': 'ir.actions.act_window',
                'target': 'new'
            }