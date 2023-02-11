import requests
import json
from datetime import datetime
from odoo.exceptions import UserError
from odoo.tools.translate import _
import logging
from odoo.addons.viettelpost_connector.common.constants import FuncName
from odoo.addons.viettelpost_connector.common.constants import Method

_logger = logging.getLogger(__name__)


class ViettelPostConnection:

    def __init__(self, host, token, external_model):
        self.host = host
        self.token = token
        self.external_model = external_model

    def execute_restful(self, func_name, method, *args, **kwargs):
        try:
            endpoint_id = self.external_model.env['api.endpoint.config'].search([('name', '=', func_name)])
            if not endpoint_id:
                raise UserError(_('Function name %s is not existed') % func_name)
            endpoint = endpoint_id.endpoint
            if func_name == FuncName.GetExtendServices:
                endpoint = endpoint.format(*args)
            url = self.host + endpoint
            headers = {
                'Content-Type': 'application/json'
            }
            if func_name != FuncName.SignIn:
                headers.update({'Token': self.token})
            if method == Method.Get:
                res = requests.get(url, params=kwargs, headers=headers, timeout=300)
            elif method == Method.Post:
                res = requests.post(url, json=kwargs, headers=headers, timeout=300)
            data = res.json()
            if isinstance(data, dict):
                if func_name == FuncName.UpdateWaybill:
                    self.update_sale_order(kwargs.get('ORDER_NUMBER', False), data.get('message', False))
                self.create_connect_history(func_name, method, url, json.dumps(kwargs), data.get('message', False), data.get('status', False))
            else:
                self.create_connect_history(func_name, method, url, json.dumps(kwargs), 'OK' if res.status_code == 200 else 'ERROR', res.status_code)
            if res.status_code != 200:
                raise UserError(_('Request failed with status: %s - Message: %s') % (res.status_code, data['message']))
            return data
        except Exception as e:
            raise e

    def update_sale_order(self, waybill_code, status):
        sale_id = self.external_model.env['sale.order'].search([('waybill_code', '=', waybill_code)])
        sale_id.write({'waybill_status': status})

    def create_connect_history(self, *args):
        create_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        uid = self.external_model.env.uid
        query = f"""
                    INSERT INTO api_connect_history (name, method, url, body, message, status, create_date, create_uid) 
                    VALUES ('{args[0]}', '{args[1]}', '{args[2]}', '{args[3]}', '{args[4]}', '{args[5]}', '{create_date}', '{uid}')
                """
        query = query.replace('\n', '')
        self.external_model.env.cr.execute(query)
        self.external_model.env.cr.commit()
