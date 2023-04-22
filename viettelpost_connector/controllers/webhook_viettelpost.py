import functools
import odoo
import json
import datetime
import re
from werkzeug.wrappers import Response

from typing import Dict, Any
from odoo import http

from odoo.addons.web.controllers.main import ensure_db
from odoo.http import Controller, request, route


STATUS_OK = 200
STATUS_BAD_REQUEST = 400
STATUS_UNAUTHORIZED = 401
STATUS_NOT_FOUND = 404


def valid_response(message: str, status: int = STATUS_OK):
    """Valid Response
    This will be return when the http request was successfully processed."""
    return {'status': 'success', 'message': message}


def invalid_response(message: str, status: int):
    """
        Invalid Response
        This will be the return value whenever the server runs into an error
        either from the client or the server.
    """
    return {'status': 'error', 'message': message}


# db_monodb = http.db_monodb


# def ensure_db(redirect='/web/database/selector'):
#     db = request.params.get('db') and request.params.get('db').strip()
#     if db and db not in http.db_filter([db]):
#         db = None
#     if not db:
#         db = db_monodb(request.httprequest)
#     return db


def validate_token(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        authorization = request.httprequest.headers.get('Authorization')
        if not authorization:
            return invalid_response('The header Authorization missing', STATUS_BAD_REQUEST)
        token = request.env['res.partner'].sudo().search([('type', '=', 'webhook_service'),
                                                         ('token', '=', authorization)])
        if not token:
            return invalid_response('The token seems to have invalid.', STATUS_NOT_FOUND)
        return func(self, *args, **kwargs)
    return wrap


class WebhookViettelpostController(Controller):

    @staticmethod
    def _validate_payload_webhook_viettelpost(payload: Dict[str, Any]):
        if not payload:
            return invalid_response(f'The payload is required.', STATUS_BAD_REQUEST)
        elif 'ORDER_NUMBER' not in payload:
            return invalid_response(f'The field ORDER_NUMBER missing.', STATUS_BAD_REQUEST)
        elif 'STATUS_NAME' not in payload:
            return invalid_response(f'The field STATUS_NAME missing.', STATUS_BAD_REQUEST)
        elif not payload.get('ORDER_NUMBER'):
            return invalid_response(f'The value of field ORDER_NUMBER is empty.', STATUS_BAD_REQUEST)
        elif not payload.get('STATUS_NAME'):
            return invalid_response(f'The value of field STATUS_NAME is empty.', STATUS_BAD_REQUEST)
        else:
            return True

    @validate_token
    @route('/api/v1/webhook/viettelpost', type='json', auth='none', methods=["POST"], csrf=False)
    def _get_webhook_viettelpost(self):
        try:
            ensure_db()
            registry = odoo.modules.registry.Registry(request.session.db)
            with odoo.api.Environment.manage(), registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                payload = request.jsonrequest.get('DATA')
                is_valid = WebhookViettelpostController._validate_payload_webhook_viettelpost(payload)
                if is_valid is not True:
                    return is_valid
                do_id = env['stock.picking'].search([('carrier_tracking_ref', '=', payload.get('ORDER_NUMBER'))])
                if not do_id:
                    return invalid_response(f'The order number {payload.get("ORDER_NUMBER")} not found.')
                do_id.write({'bl_status': payload.get('STATUS_NAME')})
                do_id.sale_id.write({
                    'order_line': [(1, )]
                })
            return valid_response('The odoo received data successfully.')
        except Exception as error:
            return invalid_response(f'Exception: {error}', STATUS_NOT_FOUND)
