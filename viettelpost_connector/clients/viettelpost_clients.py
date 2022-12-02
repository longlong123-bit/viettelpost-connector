import logging
from odoo.tools.translate import _
from odoo.exceptions import UserError
from .viettelpost_connection import ViettelPostConnection
_logger = logging.getLogger(__name__)


class ViettelPostClient:
    def __init__(self, host, token, external_model):
        self.conn = ViettelPostConnection(host, token, external_model)

    def get_provinces(self):
        res = self.conn.execute_restful('GetProvinces', 'GET')
        res = self.check_response(res)
        return res

    def get_districts(self):
        res = self.conn.execute_restful('GetDistricts', 'GET')
        res = self.check_response(res)
        return res

    def get_wards(self):
        res = self.conn.execute_restful('GetWards', 'GET')
        res = self.check_response(res)
        return res

    def sign_in(self, payload):
        res = self.conn.execute_restful('SignIn', 'POST', **payload)
        res = self.check_response(res)
        return res

    def sign_in_owner(self, payload):
        res = self.conn.execute_restful('SignInOwner', 'POST', **payload)
        res = self.check_response(res)
        return res

    def get_offices(self):
        res = self.conn.execute_restful('GetOffices', 'GET')
        res = self.check_response(res)
        return res

    def get_services(self, payload):
        res = self.conn.execute_restful('GetServices', 'POST', **payload)
        res = self.check_response(res)
        return res

    def get_extend_services(self, param):
        res = self.conn.execute_restful('GetExtendServices', 'GET', param)
        res = self.check_response(res)
        return res

    def get_stores(self):
        res = self.conn.execute_restful('GetStores', 'GET')
        res = self.check_response(res)
        return res

    def set_store(self, payload):
        res = self.conn.execute_restful('SetStore', 'POST', **payload)
        res = self.check_response(res)
        return res

    def compute_fee_ship_all(self, payload):
        res = self.conn.execute_restful('ComputeFeeAll', 'POST', **payload)
        res = self.check_response(res)
        return res

    def create_waybill(self, payload):
        res = self.conn.execute_restful('CreateWaybill', 'POST', **payload)
        res = self.check_response(res)
        return res

    def update_waybill(self, payload):
        res = self.conn.execute_restful('UpdateWaybill', 'POST', **payload)
        res = self.check_response(res)
        return res

    def print_waybill(self, payload):
        res = self.conn.execute_restful('PrintWaybill', 'POST', **payload)
        res = self.check_response_print_waybill(res)
        return res

    def check_ship_cost(self, payload):
        res = self.conn.execute_restful('CheckShipCost', 'POST', **payload)
        res = self.check_response(res)
        return res

    def check_response(self, res):
        if isinstance(res, list):
            return res
        if res['status'] == 200:
            res = res['data']
        else:
            self.error(res)
        return res

    def check_response_print_waybill(self, res):
        if res['status'] == 200:
            res = res['message']
        else:
            self.error(res)
        return res

    def error(self, data):
        _logger.error('\n%s', data)
        msg = data.get('message', _('No description error'))
        raise UserError(_('Error: %s') % msg)

