from odoo import fields, api, models, _
from odoo.exceptions import UserError

from odoo.addons.viettelpost_connector.common.constants import Const
from odoo.addons.viettelpost_connector.common.constants import Message


class ViettelPostService(models.Model):
    _name = 'viettelpost.service'
    _description = 'List ViettelPost Service'

    name = fields.Char(string='Service name')
    code = fields.Char(string='Service code')
    extend_service_ids = fields.One2many('viettelpost.extend.service', 'service_id', string='Extend Service')
    delivery_carrier_id = fields.Many2one('delivery.carrier', string='Delivery Carrier')

    @api.model
    def sync_service(self):
        client = self.env['api.connect.config'].generate_client_api()
        try:
            data_services: list = []
            delivery_carrier_id = self.env['delivery.carrier'].search(
                [('delivery_carrier_code', '=', Const.DELIVERY_CARRIER_CODE)])
            if not delivery_carrier_id:
                raise UserError(_(Message.MSG_NOT_CARRIER))
            payload: dict = {'TYPE': Const.TYPE_SERVICE}
            dataset = client.get_services(payload)
            if len(dataset) > 0:
                lst_service_ids: list = [rec.get('SERVICE_CODE') for rec in dataset]
                results = self.search([('code', 'in', lst_service_ids)])
                result_ids: list = [res.id for res in results]
                dataset = list(filter(lambda x: x.get('SERVICE_CODE') not in result_ids, dataset))
                if len(dataset) > 0:
                    for data in dataset:
                        dict_service: dict = {
                            'name': data.get('SERVICE_NAME'),
                            'code': data.get('SERVICE_CODE'),
                            'delivery_carrier_id': delivery_carrier_id.id
                        }
                        data_services.append(dict_service)
                    self.create(data_services)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Sync Service Successfully!"),
                    "type": "success",
                    "message": _(Message.MSG_ACTION_SUCCESS),
                    "sticky": False,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
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

    @api.model
    def sync_extend_services(self):
        client = self.env['api.connect.config'].generate_client_api()
        try:
            data_service_extend_ids: list = []
            lst_service_id = self.search([])
            if len(lst_service_id) > 0:
                for service in lst_service_id:
                    dataset = client.get_extend_services(service.code)
                    for data in dataset:
                        extend_service_id = self.env['viettelpost.extend.service'].search([
                            ('extend_code', '=', data.get('SERVICE_CODE')),
                            ('service_id', '=', service.id)
                        ])
                        if not extend_service_id:
                            data: dict = {
                                'extend_code': data.get('SERVICE_CODE'),
                                'extend_name': data.get('SERVICE_NAME'),
                                'service_id': service.id
                            }
                            data_service_extend_ids.append(data)
                    self.env['viettelpost.extend.service'].create(data_service_extend_ids)
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Sync Extend Service Successfully!"),
                        "type": "success",
                        "message": _(Message.MSG_ACTION_SUCCESS),
                        "sticky": False,
                        "next": {"type": "ir.actions.act_window_close"},
                    },
                }
            else:
                raise UserError(_('Please sync service before sync extend service.'))
        except Exception as e:
            raise UserError(_(f'Sync extend service failed. {e}'))


class ExtendService(models.Model):
    _name = 'viettelpost.extend.service'
    _description = 'List extend service ViettelPost'

    extend_code = fields.Char(string='Service Code')
    extend_name = fields.Char(string='Service Name')
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
