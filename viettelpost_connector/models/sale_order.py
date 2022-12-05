import base64

from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.addons.viettelpost_connector.contanst.viettelpost_contanst import Const
from odoo.addons.viettelpost_connector.contanst.viettelpost_contanst import Message
from odoo.addons.viettelpost_connector.clients.viettelpost_clients import ViettelPostClient


class SaleOrderVTPost(models.Model):
    _inherit = 'sale.order'
    _description = 'For ViettelPost'

    def _default_product_type(self):
        product_type_id = self.env['viettelpost.product.type'].search([('code', '=', Const.PRODUCT_TYPE_CODE_HH)])
        if product_type_id:
            return product_type_id

    def _default_national_type(self):
        national_type_id = self.env['viettelpost.national.type'].search([('code', '=', Const.NATIONAL_TYPE_CODE)])
        if national_type_id:
            return national_type_id

    def _default_waybill_type(self):
        waybill_type_id = self.env['viettelpost.waybill.type'].search([('code', '=', Const.WAYBILL_TYPE_CODE_1)])
        if waybill_type_id:
            return waybill_type_id

    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )
    tracking_link = fields.Char(string='Tracking link', store=False, default=Const.TRACKING_LINK, readonly=True)
    waybill_code = fields.Char(string='Waybill code', readonly=True)
    delivery_carrier_vtp_id = fields.Many2one('delivery.carrier', string='Delivery Method')
    vtp_store_id = fields.Many2one('viettelpost.store', string='Warehouse')
    vtp_product_type_id = fields.Many2one('viettelpost.product.type', string='Product type',
                                          default=_default_product_type)
    vtp_national_type_id = fields.Many2one('viettelpost.national.type', string='National type',
                                           default=_default_national_type)
    vtp_waybill_type_id = fields.Many2one('viettelpost.waybill.type', string='Waybill type',
                                          default=_default_waybill_type)
    vtp_lst_service_id = fields.Many2one('viettelpost.service', string='Service')
    vtp_lst_extent_service_id = fields.Many2one('viettelpost.extend.service', string='Extend service')
    vtp_note = fields.Text(string='Note')
    sender_fullname = fields.Char(related='vtp_store_id.name', string='Fullname')
    sender_phone = fields.Char(related='vtp_store_id.phone', string='Phone')
    sender_email = fields.Char(related='vtp_store_id.email', string='Email')
    sender_address = fields.Char(related='vtp_store_id.address', string='Street')
    sender_province_id = fields.Many2one(related='vtp_store_id.province_id', string='Province')
    sender_district_id = fields.Many2one(related='vtp_store_id.district_id', string='District')
    sender_ward_id = fields.Many2one(related='vtp_store_id.ward_id', string='Ward')
    sender_groupaddress_id = fields.Integer(related='vtp_store_id.group_address_id', string='Sender groupaddress')
    sender_cus_id = fields.Integer(related='vtp_store_id.customer_id', string='Sender customer')

    receiver_fullname = fields.Char(related='partner_id.name', string='Fullname')
    receiver_phone = fields.Char(related='partner_id.mobile', string='Phone')
    receiver_email = fields.Char(related='partner_id.email', string='Email')
    receiver_street = fields.Char(related='partner_id.vtp_street', string='Street')
    receiver_ward_id = fields.Many2one(related='partner_id.vtp_ward_id', string='Ward')
    receiver_district_id = fields.Many2one(related='partner_id.vtp_district_id', string='District')
    receiver_province_id = fields.Many2one(related='partner_id.vtp_province_id', string='Province')

    list_service_supported_ids = fields.One2many('list.service.supported', 'sale_id', string='List services supported')

    money_total = fields.Monetary(string='Money total', readonly=True)
    money_total_fee = fields.Monetary(string='Money total fee', readonly=True)
    money_fee = fields.Monetary(string='Money fee', readonly=True)
    money_collection_fee = fields.Monetary(string='Money collection fee', readonly=True)
    money_vat = fields.Monetary(string='Money VAT', readonly=True)
    actual_kpi_ht = fields.Char(string='KPI HT', readonly=True)
    exchange_weight = fields.Integer(string='Exchange weight (g)', readonly=True)
    money_collection = fields.Monetary(string='Money collection', readonly=True)
    money_other_fee = fields.Monetary(string='Money other fee', readonly=True)
    waybill_status = fields.Char(string='Waybill status', readonly=True)
    is_check_service = fields.Boolean(string='Is check service', default=False)

    @api.onchange('vtp_lst_service_id')
    def _onchange_vtp_lst_service_id(self):
        for rec in self:
            if rec.vtp_lst_service_id:
                return {
                    'domain':
                        {
                            'vtp_lst_extent_service_id': [('service_id', '=', rec.vtp_lst_service_id.id)]
                        },
                    }

    def action_create_waybill_code(self):
        server_id = self.env['api.connect.config'].search([('code', '=', Const.BASE_CODE), ('active', '=', True)])
        if not server_id:
            raise UserError(_(Message.BASE_MSG))
        client = ViettelPostClient(server_id.host, server_id.token, self)
        try:
            payload = self._prepare_data_create_waybill()
            res = client.create_waybill(payload)
            self.env['sale.order.line'].create({
                'product_id': self.delivery_carrier_vtp_id.product_id.id,
                'name': f'{self.vtp_lst_service_id.display_name}\n{self.vtp_lst_extent_service_id.display_name}'
                if self.vtp_lst_extent_service_id else f'{self.vtp_lst_service_id.display_name}',
                'product_uom_qty': 1.0,
                'price_unit': res['MONEY_TOTAL'],
                'price_subtotal': res['MONEY_TOTAL'],
                'price_total': res['MONEY_TOTAL'],
                'sequence': self.order_line[-1].sequence + 1,
                'order_id': self.order_line[-1].order_id.id,
                'is_delivery': True
            })
            self.write({
                'waybill_code': res['ORDER_NUMBER'],
                'money_collection': res['MONEY_COLLECTION'],
                'money_total': res['MONEY_TOTAL'],
                'money_total_fee': res['MONEY_TOTAL_FEE'],
                'money_fee': res['MONEY_FEE'],
                'money_collection_fee': res['MONEY_COLLECTION_FEE'],
                'money_vat': res['MONEY_VAT'],
                'actual_kpi_ht': f"{int(res['KPI_HT'])} giờ",
                'exchange_weight': res['EXCHANGE_WEIGHT'],
                'money_other_fee': res['MONEY_OTHER_FEE'],
            })
        except Exception as e:
            raise UserError(_(f'Create waybill failed. {e}'))

    def get_list_service(self):
        server_id = self.env['api.connect.config'].search([('code', '=', Const.BASE_CODE), ('active', '=', True)])
        if not server_id:
            raise UserError(_(Message.BASE_MSG))
        client = ViettelPostClient(server_id.host, server_id.token, self)
        try:
            payload = self._prepare_payload_for_get_list_service()
            res = client.compute_fee_ship_all(payload)
            for dict_service in res:
                service_id = self.env['viettelpost.service'].search([('code', '=', dict_service['MA_DV_CHINH'])])
                if not service_id:
                    new_service_id = self.env['viettelpost.service'].create({
                        'name': dict_service['TEN_DICHVU'],
                        'code': dict_service['MA_DV_CHINH']
                    })
                lst_service_id = self.env['list.service.supported'].search([
                    ('service_id', '=', service_id.id if service_id else new_service_id.id),
                    ('sale_id', '=', self.id)
                ])
                if not lst_service_id:
                    lst_service_id.create({
                        'service_id': service_id.id if service_id else new_service_id.id,
                        'money_total': dict_service['GIA_CUOC'],
                        'kpi_ht': dict_service['THOI_GIAN'],
                        'sale_id': self.id
                    })
            self.write({'is_check_service': True})
        except Exception as e:
            raise UserError(_(f'Get a list of services that match itinerary failed. {e}'))

    def _compute_weight_and_qty(self) -> (float, float):
        total_weight = 0.0
        total_qty = 0.0
        if len(self.order_line) > 0:
            for line in self.order_line:
                total_weight += line.product_id.product_tmpl_id.gross_weight
                total_qty += line.product_uom_qty
            return total_qty, total_weight
        else:
            raise UserError(_('Please add products to order line.'))

    def _prepare_data_order_line(self) -> (list, float, float):
        list_item = []
        total_weight = 0.0
        total_qty = 0.0
        total_price = 0.0
        if len(self.order_line) > 0:
            for line in self.order_line:
                gross_width = line.product_id.product_tmpl_id.gross_width
                gross_height = line.product_id.product_tmpl_id.gross_height
                gross_depth = line.product_id.product_tmpl_id.gross_depth
                weight = (gross_width * gross_height * gross_depth) / 6000
                order_line = {
                    'PRODUCT_NAME': line.product_id.product_tmpl_id.name,
                    'PRODUCT_PRICE': line.price_subtotal,
                    'PRODUCT_WEIGHT': weight,
                    'PRODUCT_QUANTITY': line.product_uom_qty
                }
                total_price += line.price_subtotal
                total_weight += weight
                total_qty += line.product_uom_qty
                list_item.append(order_line)
            return list_item, total_weight, total_qty, total_price
        else:
            raise UserError(_('Please add products to order line.'))

    def _prepare_payload_for_get_list_service(self) -> dict:
        if not self.partner_id:
            raise UserError(_('Please add customer to sale order.'))
        list_item, total_weight, total_qty, total_price = self._prepare_data_order_line()
        payload = {
            'PRODUCT_WEIGHT': total_weight,
            'PRODUCT_PRICE': total_price,
            'MONEY_COLLECTION': 0,
            'SENDER_PROVINCE': self.vtp_store_id.province_id.province_id,
            'SENDER_DISTRICT': self.vtp_store_id.district_id.district_id,
            'RECEIVER_PROVINCE': self.partner_id.vtp_province_id.province_id,
            'RECEIVER_DISTRICT': self.partner_id.vtp_district_id.district_id,
            'PRODUCT_TYPE': self.vtp_product_type_id.code,
            'TYPE': int(self.vtp_national_type_id.code)
        }
        return payload

    def _prepare_payload_check_ship_code(self):
        list_item, total_weight, total_qty, total_price = self._prepare_data_order_line()
        payload = {
            "PRODUCT_WEIGHT": total_weight,
            "PRODUCT_PRICE": total_price,
            "MONEY_COLLECTION": 0,
            "ORDER_SERVICE_ADD": self.vtp_lst_extent_service_id.extend_code or '',
            "ORDER_SERVICE": self.vtp_lst_service_id.code,
            "SENDER_PROVINCE": self.vtp_store_id.province_id.province_id,
            "SENDER_DISTRICT": self.vtp_store_id.district_id.district_id,
            "RECEIVER_PROVINCE": self.partner_id.vtp_province_id.province_id,
            "RECEIVER_DISTRICT": self.partner_id.vtp_district_id.district_id,
            "PRODUCT_TYPE": self.vtp_product_type_id.code,
            "NATIONAL_TYPE": int(self.vtp_national_type_id.code)
        }
        return payload

    def _compute_money_collection(self) -> (float, float):
        collection = 0.0
        fee = 0.0
        list_item, total_weight, total_qty, total_price = self._prepare_data_order_line()
        if self.vtp_waybill_type_id.code in [Const.WAYBILL_TYPE_CODE_2, Const.WAYBILL_TYPE_CODE_4]:
            server_id = self.env['api.connect.config'].search([('code', '=', Const.BASE_CODE), ('active', '=', True)])
            if not server_id:
                raise UserError(_(Message.BASE_MSG))
            client = ViettelPostClient(server_id.host, server_id.token, self)
            payload = self._prepare_payload_check_ship_code()
            res = client.check_ship_cost(payload)
        if self.vtp_waybill_type_id.code == Const.WAYBILL_TYPE_CODE_2:
            collection = total_price
            fee = res['MONEY_TOTAL']
        elif self.vtp_waybill_type_id.code == Const.WAYBILL_TYPE_CODE_3:
            collection = float(self.amount_untaxed)
        elif self.vtp_waybill_type_id.code == Const.WAYBILL_TYPE_CODE_4:
            collection = res['MONEY_TOTAL']
        return collection, fee

    def _prepare_data_create_waybill(self) -> dict:
        list_item, total_weight, total_qty, total_price = self._prepare_data_order_line()
        collection, money_total = self._compute_money_collection()
        lst_service_support = self.env['list.service.supported'].search([('sale_id', '=', self.id)])
        if not self.partner_id:
            raise UserError(_('Please add customer to sale order.'))
        elif not self.vtp_store_id:
            raise UserError(_('Please add a warehouse to sale order.'))
        elif not self.vtp_lst_service_id:
            raise UserError(_('Please add a service type to sale order.'))
        elif not lst_service_support:
            raise UserError(_('Please get a list of services that match itinerary'))
        elif not self.vtp_product_type_id:
            raise UserError(_('Please add a product type to sale order.'))
        elif not self.vtp_national_type_id:
            raise UserError(_('Please add a national type to sale order.'))
        elif not self.vtp_waybill_type_id:
            raise UserError(_('Please add a waybill type to sale order.'))
        code_service_support = [rec.service_id.code for rec in lst_service_support]
        if self.vtp_lst_service_id.code not in code_service_support:
            raise UserError(_('Please choose a service in list of services that match itinerary'))
        payload = {
            'ORDER_NUMBER': self.name,
            'GROUPADDRESS_ID': self.vtp_store_id.group_address_id,
            'CUS_ID': self.vtp_store_id.customer_id,
            'DELIVERY_DATE': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'SENDER_FULLNAME': self.vtp_store_id.name,
            'SENDER_ADDRESS': self.vtp_store_id.address,
            'SENDER_PHONE': self.vtp_store_id.phone or '',
            'SENDER_EMAIL': self.vtp_store_id.email or '',
            'SENDER_WARD': self.vtp_store_id.ward_id.ward_id,
            'SENDER_DISTRICT': self.vtp_store_id.district_id.district_id,
            'SENDER_PROVINCE': self.vtp_store_id.province_id.province_id,
            'SENDER_LATITUDE': 0,
            'SENDER_LONGITUDE': 0,
            'RECEIVER_FULLNAME': self.partner_id.name,
            'RECEIVER_ADDRESS': self.partner_id.vtp_street,
            'RECEIVER_PHONE': self.partner_id.mobile or '',
            'RECEIVER_EMAIL': self.partner_id.email or '',
            'RECEIVER_WARD': self.partner_id.vtp_ward_id.ward_id,
            'RECEIVER_DISTRICT': self.partner_id.vtp_district_id.district_id,
            'RECEIVER_PROVINCE': self.partner_id.vtp_province_id.province_id,
            'RECEIVER_LATITUDE': 0,
            'RECEIVER_LONGITUDE': 0,
            'PRODUCT_NAME': self.order_line[0].product_id.product_tmpl_id.name,
            'PRODUCT_DESCRIPTION': self.order_line[0].product_id.product_tmpl_id.name,
            'PRODUCT_QUANTITY': total_qty,
            'PRODUCT_PRICE': total_price,
            'PRODUCT_WEIGHT': int(total_weight) or 0,
            'PRODUCT_TYPE': self.vtp_product_type_id.code,
            'ORDER_PAYMENT': int(self.vtp_waybill_type_id.code),
            'ORDER_SERVICE': self.vtp_lst_service_id.code,
            'ORDER_SERVICE_ADD': self.vtp_lst_extent_service_id.extend_code or '',
            'ORDER_VOUCHER': '',
            'ORDER_NOTE': self.vtp_note or '',
            'MONEY_COLLECTION': collection,
            "MONEY_TOTAL": money_total,
            # "CHECK_UNIQUE": True,
            'LIST_ITEM': list_item
        }
        return payload


class ComputedFeeShip(models.Model):
    _name = 'list.service.supported'
    _description = 'List services supported'
    _rec_name = 'service_id'

    sale_id = fields.Many2one('sale.order', string='Sale order')
    currency_id = fields.Many2one('res.currency', related='sale_id.currency_id')
    service_id = fields.Many2one('viettelpost.service', string='Service')
    money_total = fields.Monetary(string='Total')
    kpi_ht = fields.Char(string='Deadline')
