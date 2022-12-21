from odoo import models, _
from odoo.exceptions import UserError
from odoo.addons.viettelpost_connector.contanst.viettelpost_contanst import Const
from odoo.addons.viettelpost_connector.contanst.viettelpost_contanst import Message


class StockPickingVTP(models.Model):
    _inherit = 'stock.picking'
    _description = 'For ViettelPost'

    def action_confirm_waybill(self):
        client = self.env['api.connect.config'].generate_client_api()
        try:
            payload = self._prepare_payload_update_waybill(Const.VTP_STATUS_TYPE_1, Message.NOTE_CONFIRM_ORDER)
            client.update_waybill(payload)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Confirm waybill successfully!"),
                    "type": "success",
                    "message": _(Message.NOTE_WAITING_SHIPPER),
                    "sticky": False,
                },
            }
        except Exception as e:
            raise UserError(_(f'Confirm waybill failed. {e}'))

    def action_cancel(self):
        res = super(StockPickingVTP, self).action_cancel()
        client = self.env['api.connect.config'].generate_client_api()
        try:
            payload = self._prepare_payload_update_waybill(Const.VTP_STATUS_TYPE_4, Message.NOTE_CANCEL_ORDER)
            client.update_waybill(payload)
            return res
        except Exception as e:
            raise UserError(_(f'Cancel waybill failed. {e}'))

    def _prepare_payload_update_waybill(self, type_update, note) -> dict:
        if not self.sale_id.waybill_code:
            raise UserError(_('The waybill code not found.'))
        if not type_update:
            raise UserError(_('The type function not found.'))
        payload = {
            "TYPE": type_update,
            "ORDER_NUMBER": self.sale_id.waybill_code,
            "NOTE": note
        }
        return payload