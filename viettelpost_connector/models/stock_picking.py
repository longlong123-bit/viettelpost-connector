from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.addons.viettelpost_connector.common.constants import Const, Message


class StockPickingVTP(models.Model):
    _inherit = 'stock.picking'
    _description = 'For ViettelPost'

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    money_total = fields.Monetary(string='Money total', readonly=True, currency_field='currency_id')
    money_total_fee = fields.Monetary(string='Money total fee', readonly=True, currency_field='currency_id')
    money_fee = fields.Monetary(string='Money fee', readonly=True, currency_field='currency_id')
    money_collection_fee = fields.Monetary(string='Money collection fee', readonly=True,
                                           currency_field='currency_id')
    money_vat = fields.Monetary(string='Money VAT', readonly=True, currency_field='currency_id')
    money_collection = fields.Monetary(string='Money collection', readonly=True, currency_field='currency_id')
    money_other_fee = fields.Monetary(string='Money other fee', readonly=True, currency_field='currency_id')
    bl_status = fields.Char(string='Waybill status', readonly=True, tracking=True)
    carrier_tracking_ref = fields.Char(string='Tracking Reference', copy=False, tracking=True)

    def _compute_carrier_tracking_url(self):
        res = super(StockPickingVTP, self)._compute_carrier_tracking_url()
        for rec in self:
            if not rec.carrier_tracking_url and rec.carrier_id.delivery_type == 'viettelpost':
                rec.carrier_tracking_url = Const.TRACKING_LINK.format(bl_code=rec.carrier_tracking_ref)
        return res
    
    def button_validate(self):
        try:
            if self.carrier_id.delivery_type == 'viettelpost':
                if not self.carrier_tracking_ref:
                    raise UserError(_('The carrier tracking ref is required'))
                self._update_shipment_viettelpost(Const.VTP_STATUS_TYPE_1, Message.NOTE_CONFIRM_ORDER)
            res = super(StockPickingVTP, self).button_validate()
            return res
        except Exception as e:
            raise UserError(_(f'Confirm waybill failed. {e}'))

    def cancel_shipment(self):
        try:
            if self.carrier_id.delivery_type == 'viettelpost':
                if not self.carrier_tracking_ref:
                    raise UserError(_('The carrier tracking ref is required'))
                self._update_shipment_viettelpost(Const.VTP_STATUS_TYPE_4, Message.NOTE_CANCEL_ORDER)
            res = super(StockPickingVTP, self).cancel_shipment()
            return res
        except Exception as e:
            raise UserError(_(f'Cancel waybill failed. {e}'))

    def _prepare_payload_update_waybill(self, type_update: str, note: str) -> dict:
        if not self.carrier_tracking_ref:
            raise UserError(_('The carrier tracking ref not found.'))
        if not type_update:
            raise UserError(_('The type function not found.'))
        payload: dict = {
            'TYPE': type_update,
            'ORDER_NUMBER': self.carrier_tracking_ref,
            'NOTE': note
        }
        return payload

    def _update_shipment_viettelpost(self, type_update: str, message: str) -> None:
        client = self.env['api.connect.instances'].generate_client_api()
        payload = self._prepare_payload_update_waybill(type_update, message)
        client.update_waybill(payload)