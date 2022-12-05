from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import ustr
import logging
import requests
_logger = logging.getLogger(__name__)
from odoo.addons.viettelpost_connector.clients.viettelpost_clients import ViettelPostClient
from odoo.addons.viettelpost_connector.contanst.viettelpost_contanst import Const
from odoo.addons.viettelpost_connector.contanst.viettelpost_contanst import Message


class ApiConnectConfig(models.Model):
    _name = 'api.connect.config'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'The config server information for API Viettel Post'

    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', required=True, tracking=True)
    host = fields.Char(string='Host', required=True, tracking=True)
    token = fields.Text(string='Token', tracking=True, readonly=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    user_name = fields.Char(string='Username', tracking=True)
    password = fields.Char(string='Password', tracking=True)
    endpoint_ids = fields.One2many('api.endpoint.config', 'api_connect_config_id', string='Endpoint')

    def btn_test_connection(self):
        self.ensure_one()
        try:
            request = requests.get(self.host, timeout=3)
            _logger.info(f'{request}')
        except UserError as e:
            raise e
        except Exception as e:
            raise UserError(_(f'Connection Test Failed! Here is what we got instead:\n {ustr(e)}'))
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Connection test successfully!"),
                "type": "success",
                "message": _("Everything seems properly set up!"),
                "sticky": False,
            },
        }

    def get_owner_token(self):
        server_id = self.env['api.connect.config'].search([('code', '=', Const.BASE_CODE), ('active', '=', True)])
        if not server_id:
            raise UserError(_(Message.BASE_MSG))
        client = ViettelPostClient(server_id.host, server_id.token, self)
        if not self.user_name:
            raise UserError(_('Username not found.'))
        if not self.password:
            raise UserError(_('Password not found.'))
        payload = {
            'USERNAME': self.user_name,
            'PASSWORD': self.password
        }
        res = client.sign_in(payload)
        self.get_token_long_term(payload, res['token'])

    def get_token_long_term(self, payload, token):
        server_id = self.env['api.connect.config'].search([('code', '=', Const.BASE_CODE), ('active', '=', True)])
        if not server_id:
            raise UserError(_(Message.BASE_MSG))
        client = ViettelPostClient(server_id.host, token, self)
        res = client.sign_in_owner(payload)
        self.write({'token': res['token']})


class ApiConnectHistory(models.Model):
    _name = 'api.connect.history'
    _description = 'Logging request api to ViettelPost'
    _order = 'create_date desc'

    name = fields.Char(string='Request')
    status = fields.Integer(string='Status')
    message = fields.Char(string='Message')
    url = fields.Char(string='Url')
    method = fields.Char(string='Method')
    body = fields.Text(string='Body')


class ApiEndpointConfig(models.Model):
    _name = 'api.endpoint.config'
    _description = 'Configuration dynamic endpoint for host when there is a change of routes from ViettelPost. '

    endpoint = fields.Char(string='Endpoint', required=True)
    name = fields.Char(string='Function name', required=True, readonly=True)
    api_connect_config_id = fields.Many2one('api.connect.config', string='Api connect config id')
    host = fields.Char(related='api_connect_config_id.host', string='Host')
    description = fields.Text(string='Description')
