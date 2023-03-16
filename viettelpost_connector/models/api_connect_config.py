import logging
import requests

from odoo import fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import ustr

from odoo.addons.viettelpost_connector.api.clients import Client
from odoo.addons.viettelpost_connector.common.constants import Const
from odoo.addons.viettelpost_connector.common.constants import Message

_logger = logging.getLogger(__name__)


class ApiConnectConfig(models.Model):
    _name = 'api.connect.config'
    _inherit = ['mail.thread']
    _description = 'The config server information for API'

    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', required=True, tracking=True)
    domain = fields.Char(string='Domain', required=True, tracking=True)
    token = fields.Text(string='Token', tracking=True, readonly=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    username = fields.Char(string='Username', tracking=True)
    password = fields.Char(string='Password', tracking=True)
    endpoint_ids = fields.One2many('api.endpoint.config', 'api_connect_config_id', string='Endpoints')

    _sql_constraints = [
        ('name_code_domain_uniq', 'unique (name, code, domain)', "Instances server already exists!"),
    ]

    def action_test_connection(self):
        self.ensure_one()
        try:
            request = requests.get(self.domain, timeout=3)
            _logger.info(f'{request}')
        except UserError as e:
            raise e
        except Exception as e:
            raise UserError(_(f'Connection test failed! Here is what we got instead:\n {ustr(e)}'))
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Connection test successfully!'),
                'type': 'success',
                'message': _('Everything seems properly set up!'),
                'sticky': False,
            },
        }

    def generate_client_api(self):
        server_id = self.search([('code', '=', Const.BASE_CODE), ('active', '=', True)])
        if not server_id:
            raise ValidationError(_(Message.BASE_MSG))
        client = Client(server_id.domain, server_id.token, self)
        return client

    def get_owner_token(self):
        client = self.generate_client_api()
        if not self.username:
            raise ValidationError(_('Username not found.'))
        if not self.password:
            raise ValidationError(_('Password not found.'))
        payload: dict = {
            'USERNAME': self.username,
            'PASSWORD': self.password
        }
        res = client.sign_in(payload)
        token: str or bool = res.get('token', False)
        if not token:
            raise UserError(_('Get token failed.'))
        self.get_token_long_term(payload, token)

    def get_token_long_term(self, payload: dict, token: str):
        server_id = self.search([('code', '=', Const.BASE_CODE), ('active', '=', True)])
        if not server_id:
            raise ValidationError(_(Message.BASE_MSG))
        client = Client(server_id.domain, token, self)
        res = client.sign_in_owner(payload)
        self.write({'token': res.get('token')})


class ApiConnectHistory(models.Model):
    _name = 'api.connect.history'
    _description = 'Logging request API'
    _order = 'create_date desc'

    name = fields.Char(string='Request')
    status = fields.Integer(string='Status')
    message = fields.Char(string='Message')
    url = fields.Char(string='Url')
    method = fields.Char(string='Method')
    body = fields.Text(string='Body')


class ApiEndpointConfig(models.Model):
    _name = 'api.endpoint.config'
    _description = 'Configuration dynamic endpoint for domain when there is a change of routes. '

    endpoint = fields.Char(string='Endpoint', required=True)
    name = fields.Char(string='Function name', required=True, readonly=True)
    api_connect_config_id = fields.Many2one('api.connect.config', string='Api connect config id')
    domain = fields.Char(related='api_connect_config_id.domain', string='Domain')
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('name_endpoint_uniq', 'unique (name, endpoint)', "Endpoint already exists!"),
    ]
