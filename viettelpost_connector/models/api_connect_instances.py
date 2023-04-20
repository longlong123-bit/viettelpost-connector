from typing import Dict, Optional, NoReturn
from odoo import models, _
from odoo.exceptions import UserError

from odoo.addons.viettelpost_connector.api.viettelpost_clients import ViettelPostClient
from odoo.addons.viettelpost_connector.common.constants import Const
from odoo.addons.viettelpost_connector.common.constants import Message


class APIConnectInstances(models.Model):
    _inherit = 'api.connect.instances'
    _description = 'The config server information for API Instance Viettelpost'

    def generate_client_api(self) -> ViettelPostClient:
        instance_id = self.search([('code', '=', Const.INSTANCE_CODE), ('active', '=', True)])
        if not instance_id:
            raise UserError(_(Message.BASE_MSG))
        client = ViettelPostClient(instance_id.host, instance_id.token, self)
        return client

    def get_owner_token(self) -> NoReturn:
        client = self.generate_client_api()
        if not self.user_name:
            raise UserError(_('Username not found.'))
        if not self.password:
            raise UserError(_('Password not found.'))
        payload: Dict[str, str] = {
            'USERNAME': self.user_name,
            'PASSWORD': self.password
        }
        res = client.sign_in(payload)
        token: Optional[str] = res.get('token', False)
        if not token:
            raise UserError(_('Get token failed.'))
        self.get_token_long_term(payload, token)

    def get_token_long_term(self, payload: dict, token: str) -> NoReturn:
        instance_id = self.search([('code', '=', Const.INSTANCE_CODE), ('active', '=', True)])
        if not instance_id:
            raise UserError(_('The instance Viettelpost not found.'))
        client = ViettelPostClient(instance_id.host, token, self)
        res = client.sign_in_owner(payload)
        token: Optional[str] = res.get('token', False)
        if not token:
            raise UserError(_('Get token failed.'))
        self.write({'token': token})
