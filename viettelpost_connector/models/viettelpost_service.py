from typing import Dict, List
from odoo import fields, api, models, _
from odoo.exceptions import UserError

from odoo.addons.viettelpost_connector.common.constants import Const, Message
from odoo.addons.viettelpost_connector.dataclass.viettelpost_service import Service, ServiceExtend
from odoo.addons.viettelpost_connector.common.action import Action


class ViettelPostService(models.Model):
    _name = 'viettelpost.service'
    _description = 'List ViettelPost Service'

    name = fields.Char(string='Service name')
    code = fields.Char(string='Service code')
    extend_service_ids = fields.One2many('viettelpost.extend.service', 'service_id', string='Extend Service')

    @api.model
    def sync_service(self):
        try:
            client = self.env['api.connect.instances'].generate_client_api()
            data_services: list = []
            payload: Dict[str, int] = {'TYPE': Const.TYPE_SERVICE}
            result = client.get_services(payload)
            if result:
                lst_dataclass_service: List[Service] = [Service(*Service.parser_dict(res)) for res in result]
                lst_service_ids = self.search([('code', 'in', [rec.code for rec in lst_dataclass_service])])
                service_codes: List[str] = [rec.code for rec in lst_service_ids]
                for data in lst_dataclass_service:
                    if data.code not in service_codes:
                        data_services.append(Service.parser_class(data))
                if data_services:
                    service_ids = self.create(data_services)
                    self.sync_extend_services(client, service_ids)
            return Action.display_notification(_('Sync service successfully!'), _(Message.MSG_ACTION_SUCCESS))
        except Exception as e:
            raise UserError(_(f'Sync service failed. Error: {str(e)}'))

    @api.depends('name', 'code')
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.code:
                name = f'[{record.code}] - {name}'
            res.append((record.id, name))
        return res

    def sync_extend_services(self, client, service_ids):
        try:
            data_service_extend_ids: list = []
            for service in service_ids:
                result = client.get_extend_services(service.code)
                if result:
                    lst_dataclass_service_extend: List[ServiceExtend] = [ServiceExtend(*ServiceExtend.parser_dict(res)) for res in result]
                    extend_service_id = self.env['viettelpost.extend.service'].search([
                        ('extend_code', 'in', [service.code for service in lst_dataclass_service_extend]),
                        ('service_id', '=', service.id)
                    ])
                    service_extend_codes: List[str] = [service.code for service in extend_service_id]
                    for data in lst_dataclass_service_extend:
                        if data.code not in service_extend_codes:
                            data_service_extend_ids.append(ServiceExtend.parser_class(data, service_id=service.id))
            if data_service_extend_ids:
                self.env['viettelpost.extend.service'].create(data_service_extend_ids)
        except Exception as e:
            raise UserError(_(f'Sync extend service failed. {e}'))


class ExtendService(models.Model):
    _name = 'viettelpost.extend.service'
    _description = 'List extend service ViettelPost'

    extend_code = fields.Char(string='Code')
    extend_name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    service_id = fields.Many2one('viettelpost.service', string='Service')

    @api.depends('extend_name', 'extend_code')
    def name_get(self):
        res = []
        for record in self:
            extend_name = record.extend_name
            if record.extend_code:
                extend_name = f'[{record.extend_code}] - {extend_name}'
            res.append((record.id, extend_name))
        return res
