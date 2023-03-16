import logging
from odoo.tools.translate import _
from odoo.exceptions import UserError
from .connection import Connection
from odoo.addons.viettelpost_connector.common.constants import FuncName
from odoo.addons.viettelpost_connector.common.constants import Method
_logger = logging.getLogger(__name__)


class Client:
    def __init__(self, domain, token, external_model):
        self.conn = Connection(domain, token, external_model)

    def get_provinces(self):
        res = self.conn.execute_restful(FuncName.GetProvinces, Method.Get)
        res = self.check_response(res)
        return res

    def get_districts(self):
        res = self.conn.execute_restful(FuncName.GetDistricts, Method.Get)
        res = self.check_response(res)
        return res

    def get_wards(self):
        res = self.conn.execute_restful(FuncName.GetWards, Method.Get)
        res = self.check_response(res)
        return res

    def sign_in(self, payload):
        res = self.conn.execute_restful(FuncName.SignIn, Method.Post, **payload)
        res = self.check_response(res)
        return res

    def sign_in_owner(self, payload):
        res = self.conn.execute_restful(FuncName.SignInOwner, Method.Post, **payload)
        res = self.check_response(res)
        return res

    def get_offices(self):
        res = self.conn.execute_restful(FuncName.GetOffices, Method.Get)
        res = self.check_response(res)
        return res

    def get_services(self, payload):
        res = self.conn.execute_restful(FuncName.GetServices, Method.Post, **payload)
        res = self.check_response(res)
        return res

    def get_extend_services(self, param):
        res = self.conn.execute_restful(FuncName.GetExtendServices, Method.Get, param)
        res = self.check_response(res)
        return res

    def get_stores(self):
        res = self.conn.execute_restful(FuncName.GetStores, Method.Get)
        res = self.check_response(res)
        return res

    def set_store(self, payload):
        res = self.conn.execute_restful(FuncName.SetStore, Method.Post, **payload)
        res = self.check_response(res)
        return res

    def compute_fee_ship_all(self, payload):
        res = self.conn.execute_restful(FuncName.ComputeFeeAll, Method.Post, **payload)
        res = self.check_response(res)
        return res

    def create_waybill(self, payload):
        res = self.conn.execute_restful(FuncName.CreateWaybill, Method.Post, **payload)
        res = self.check_response(res)
        return res

    def check_ship_cost(self, payload):
        res = self.conn.execute_restful(FuncName.CheckShipCost, Method.Post, **payload)
        res = self.check_response(res)
        return res

    def update_waybill(self, payload):
        res = self.conn.execute_restful(FuncName.UpdateWaybill, Method.Post, **payload)
        res = self.check_response(res)
        return res

    def print_waybill(self, payload):
        res = self.conn.execute_restful(FuncName.PrintWaybill, Method.Post, **payload)
        res = self.check_response_print_waybill(res)
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

