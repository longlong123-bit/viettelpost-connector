import base64
from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.addons.viettelpost_connector.common.constants import Const
from odoo.addons.viettelpost_connector.common.constants import Message
import time
from selenium import webdriver
from selenium.webdriver.common.by import By


class PrintWaybillWizard(models.Model):
    _name = 'print.waybill.wizard'
    _description = 'Print waybill wizard'

    @api.model
    def default_get(self, fields_list):
        values = super(PrintWaybillWizard, self).default_get(fields_list)
        if not values.get('picking_id') and 'active_model' in self._context and self._context[
            'active_model'] == 'stock.picking':
            values['picking_id'] = self._context.get('active_id')
        return values

    picking_id = fields.Many2one('stock.picking', string='Delivery order', readonly=1)
    sale_id = fields.Many2one('sale.order', related='picking_id.sale_id', string='Sale order')
    waybill_code = fields.Char(related='picking_id.sale_id.waybill_code', string='Waybill code')

    def action_print_waybill(self):
        client = self.env['api.connect.instances'].generate_client_api()
        try:
            payload = self._prepare_data_print_waybill()
            token = client.print_waybill(payload)
            type_print = self.env.context.get('type_print')
            if type_print == Const.VTP_PRINT_TYPE_A5:
                url = Const.VTP_PRINT_URL_A5.format(token)
            elif type_print == Const.VTP_PRINT_TYPE_A6:
                url = Const.VTP_PRINT_URL_A6.format(token)
            elif type_print == Const.VTP_PRINT_TYPE_A7:
                url = Const.VTP_PRINT_URL_A7.format(token)
            options = webdriver.ChromeOptions()
            Driver = webdriver.Chrome(options=options)
            Driver.get(url)
            img = Driver.find_elements(By.TAG_NAME, 'img')[0].screenshot_as_png
            data_do: dict = {
                'name': f'{self.picking_id.sale_id.name}.png',
                'res_model': self.picking_id._name,
                'res_id': self.picking_id.id,
                'datas': base64.b64encode(img)
            }
            data_so: dict = {
                'name': f'{self.picking_id.sale_id.name}.png',
                'res_model': self.picking_id.sale_id._name,
                'res_id': self.picking_id.sale_id.id,
                'datas': base64.b64encode(img)
            }
            self.env['ir.attachment'].sudo().create([data_do, data_so])
            time.sleep(2)
        except Exception as e:
            raise UserError(_(f'Print waybill failed. {e}'))

    def _prepare_data_print_waybill(self) -> dict:
        payload: dict = {
            "ORDER_ARRAY": [self.picking_id.sale_id.waybill_code],
            "EXPIRY_TIME": int((datetime.utcnow() + timedelta(hours=1)).timestamp()) * 1000,
        }
        return payload