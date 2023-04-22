import base64
import io
import requests

from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.addons.viettelpost_connector.common.constants import Const
import time
from selenium import webdriver
from selenium.webdriver.common.by import By


class PrintWaybillWizard(models.Model):
    _name = 'print.waybill.wizard'
    _description = 'Print waybill wizard'

    @api.model
    def default_get(self, fields_list):
        values = super(PrintWaybillWizard, self).default_get(fields_list)
        if not values.get('picking_id') and 'active_model' in self._context \
                and self._context['active_model'] == 'stock.picking':
            values['picking_id'] = self._context.get('active_id')
        return values

    picking_id = fields.Many2one('stock.picking', string='Delivery Order', readonly=1)
    waybill_code = fields.Char(related='picking_id.carrier_tracking_ref', string='Carrier Tracking Ref')

    def _get_template_print_carrier_tracking_ref(self, mode='pdf'):
        report = self.env.ref('viettelpost_connector.action_print_carrier_tracking_ref')
        if mode == 'pdf':
            content, __ = report.render_qweb_pdf(self.id)
        else:
            content, __ = report.render_qweb_html(self.id)
        return content, report

    def action_print_waybill(self):
        try:
            if not self.picking_id.carrier_tracking_ref:
                raise UserError(_('The carrier tracking ref not found.'))
            client = self.env['api.connect.instances'].generate_client_api()
            payload = self._prepare_data_print_waybill()
            token = client.print_waybill(payload)
            type_print = self.env.context.get('type_print')
            if type_print == Const.VTP_PRINT_TYPE_A5:
                url = Const.VTP_PRINT_URL_A5.format(token)
            elif type_print == Const.VTP_PRINT_TYPE_A6:
                url = Const.VTP_PRINT_URL_A6.format(token)
            elif type_print == Const.VTP_PRINT_TYPE_A7:
                url = Const.VTP_PRINT_URL_A7.format(token)
            else:
                raise UserError(_('Print type not found.'))
            options = webdriver.ChromeOptions()
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            img = driver.find_elements(By.TAG_NAME, 'img')[0].screenshot_as_png
            data_do: dict = {
                'name': f'{self.picking_id.carrier_tracking_ref}.png',
                'res_model': self.picking_id._name,
                'res_id': self.picking_id.id,
                'datas': base64.b64encode(img)
            }
            data_so: dict = {
                'name': f'{self.picking_id.carrier_tracking_ref}.png',
                'res_model': self.picking_id.sale_id._name,
                'res_id': self.picking_id.sale_id.id,
                'datas': base64.b64encode(img)
            }
            self.env['ir.attachment'].sudo().create([data_do, data_so])
        except Exception as e:
            raise UserError(_(f'Print waybill failed. {e}'))

    def _prepare_data_print_waybill(self) -> dict:
        payload: dict = {
            "ORDER_ARRAY": [self.picking_id.carrier_tracking_ref],
            "EXPIRY_TIME": int((datetime.utcnow() + timedelta(hours=1)).timestamp()) * 1000,
        }
        return payload