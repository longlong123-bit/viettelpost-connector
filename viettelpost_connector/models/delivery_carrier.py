from odoo import fields, models, _


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'
    _description = 'Configuration ViettelPost Carrier'

    delivery_type = fields.Selection(selection_add=[('viettelpost', 'Viettelpost')])

    @staticmethod
    def viettelpost_send_shipping(pickings):
        res = []
        for p in pickings:
            res = res + [{'exact_price': p.carrier_id.fixed_price, 'tracking_number': False}]
        return res

    def viettelpost_rate_shipment(self, order):
        carrier = self._match_address(order.partner_shipping_id)
        if not carrier:
            return {
                'success': False,
                'price': 0.0,
                'error_message': _('Error: this delivery method is not available for this address.'),
                'warning_message': False
            }
        price = self.fixed_price
        company = self.company_id or order.company_id or self.env.company
        if company.currency_id and company.currency_id != order.currency_id:
            price = company.currency_id._convert(price, order.currency_id, company, fields.Date.today())
        return {
            'success': True,
            'price': price,
            'error_message': False,
            'warning_message': False
        }
