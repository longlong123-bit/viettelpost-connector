import re
from typing import Optional, Dict, Any
from datetime import date, datetime
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

from odoo.addons.viettelpost_connector.common.constants import Message


class AccountPaymentWizard(models.TransientModel):
    _name = 'account.payment.wizard'
    _description = 'Register payment'
    _rec_name = 'voucher_sequence'

    MONTH_SELECTION = [
        ('01', 'Tháng 01'),
        ('02', 'Tháng 02'),
        ('03', 'Tháng 03'),
        ('04', 'Tháng 04'),
        ('05', 'Tháng 05'),
        ('06', 'Tháng 06'),
        ('07', 'Tháng 07'),
        ('08', 'Tháng 08'),
        ('09', 'Tháng 09'),
        ('10', 'Tháng 10'),
        ('11', 'Tháng 11'),
        ('12', 'Tháng 12'),
    ]

    @api.model
    def action_register_payment(self):
        action = self.env.ref('viettelpost_connector.register_payment_wizard_action').read()[0]
        return action

    date_voucher = fields.Date(string='Date Voucher', default=lambda self: date.today(), required=True)
    partner_id = fields.Many2one('res.partner', 'Object/Customer', required=True)
    partner_address = fields.Char(related='partner_id.vtp_address', string='Address')
    prepared_by_id = fields.Many2one('res.users', string='Prepared by', required=True, default=lambda self: self.env.uid)
    reason = fields.Text(string='Reason', required=True)
    object_receipt_payment = fields.Text(string='Receipt/Payment Object')
    month_of_payment_period = fields.Selection(MONTH_SELECTION, default='01')
    year_of_payment_period = fields.Char()
    payment_amount = fields.Integer(string='Amount', currency_field='currency_id')
    payment_type = fields.Selection([
        ('outbound', 'Send'),
        ('inbound', 'Receive'),
    ], string='Payment Type', default='inbound', required=True)

    def _get_sequence_receipt(self):
        sequence = self.env['ir.sequence'].search([
            ('code', '=', 'account.payment.wizard'),
            ('prefix', '=', 'PT')
        ])
        next_document = sequence.get_next_char(sequence.number_next_actual)
        self._cr.execute('''SELECT voucher_sequence FROM account_payment''')
        query_res = self._cr.fetchall()
        while next_document in [res[0] for res in query_res]:
            next_tmp = self.env['ir.sequence'].next_by_code('account.payment.wizard')
            next_document = next_tmp
        return next_document

    def _get_sequence_payment(self):
        sequence = self.env['ir.sequence'].search([
            ('code', '=', 'account.payment.wizard'),
            ('prefix', '=', 'PC')
        ])
        next_document = sequence.get_next_char(sequence.number_next_actual)
        self._cr.execute('''SELECT voucher_sequence FROM account_payment''')
        query_res = self._cr.fetchall()
        while next_document in [res[0] for res in query_res]:
            next_tmp = self.env['ir.sequence'].next_by_code('account.payment.wizard')
            next_document = next_tmp
        return next_document

    def _get_default_sequence(self):
        next_sequence = self._get_sequence_receipt()
        return next_sequence

    def _get_default_journal(self):
        cash_id = self.env['account.journal'].search([('type', '=', 'cash')])
        return cash_id.id

    voucher_sequence = fields.Char(string='Voucher', required=True, default=_get_default_sequence)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, default=_get_default_journal)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    incurred_customer_debts = fields.Monetary(string='Incurred customer debts', currency_field='currency_id')
    payment_category_id = fields.Many2one('payment.category', string='Category', required=True)
    payment_method_line_id = fields.Many2one('account.payment.method.line', string='Payment Method',
                                             readonly=False, store=True, copy=False,
                                             compute='_compute_payment_method_line_id',
                                             domain="[('id', 'in', available_payment_method_line_ids)]")
    available_payment_method_line_ids = fields.Many2many('account.payment.method.line',
                                                         compute='_compute_payment_method_line_fields')
    hide_payment_method_line = fields.Boolean(compute='_compute_payment_method_line_fields')

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        for rec in self:
            domain = dict()
            if rec.payment_type:
                if rec.payment_type == 'inbound':
                    domain = {'payment_category_id': [('category', '=', 'receipt')]}
                    rec.voucher_sequence = self._get_sequence_receipt()
                else:
                    domain = {'payment_category_id': [('category', '=', 'payment')]}
                    rec.voucher_sequence = self._get_sequence_payment()
            return {'domain': domain}

    @api.depends('available_payment_method_line_ids')
    def _compute_payment_method_line_id(self):
        for pay in self:
            available_payment_method_lines = pay.available_payment_method_line_ids
            if pay.payment_method_line_id in available_payment_method_lines:
                pay.payment_method_line_id = pay.payment_method_line_id
            elif available_payment_method_lines:
                pay.payment_method_line_id = available_payment_method_lines[0]._origin
            else:
                pay.payment_method_line_id = False

    @api.depends('payment_type', 'journal_id')
    def _compute_payment_method_line_fields(self):
        for pay in self:
            pay.available_payment_method_line_ids = pay.journal_id._get_available_payment_method_lines(pay.payment_type)
            to_exclude = pay._get_payment_method_codes_to_exclude()
            if to_exclude:
                pay.available_payment_method_line_ids = pay.available_payment_method_line_ids.filtered(
                    lambda x: x.code not in to_exclude)
            if pay.payment_method_line_id.id not in pay.available_payment_method_line_ids.ids:
                pay.hide_payment_method_line = False
            else:
                pay.hide_payment_method_line = len(
                    pay.available_payment_method_line_ids) == 1 and pay.available_payment_method_line_ids.code == 'manual'

    def _get_payment_method_codes_to_exclude(self):
        self.ensure_one()
        return []

    @api.onchange('year_of_payment_period')
    def _onchange_validated_year(self):
        if self.year_of_payment_period:
            if not re.match("^\d{4}$", self.year_of_payment_period):
                raise UserError(_("Invalid year!"))

    def _prepare_data_payment_vals_from_wizard(self) -> Dict[str, Any]:
        payment_vals = {
            'date': self.date_voucher,
            'amount': self.payment_amount,
            'payment_type': self.payment_type,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'reason': self.reason,
            'prepared_by_id': self.prepared_by_id.id,
            'object_receipt_payment': self.object_receipt_payment,
            'voucher_sequence': self.voucher_sequence,
            'payment_category_id': self.payment_category_id.id
        }
        return payment_vals

    def register_payment(self):
        payment_vals = self._prepare_data_payment_vals_from_wizard()
        account_payment = self.env['account.payment'].sudo().create(payment_vals)
        account_payment.action_post()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Account payment',
            'res_model': 'account.payment',
            'view_mode': 'form',
            'res_id': account_payment.id,
            'target': 'current',
        }

    @staticmethod
    def is_leap_year(year: int) -> bool:
        is_valid_year = True if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0 else False
        return is_valid_year

    def _get_sum_money_total_sale_orders(self, date_from: str, date_to: str, partner_id: int) -> Optional[float]:
        self._cr.execute(f'''
                            SELECT SUM(COALESCE(money_total, 0)) FROM sale_order 
                            WHERE partner_id = {partner_id}
                            AND date_order BETWEEN {date_from} AND {date_to};
                        ''')
        query_res = self._cr.fetchall()
        return query_res[0][0]

    def _get_sum_paid_money_payments(self, date_from: str, date_to: str, partner_id: int) -> Optional[float]:
        self._cr.execute(f'''
                            SELECT SUM(COALESCE(amount, 0)) FROM account_payment ACP
                            JOIN account_move ACM ON ACP.move_id = ACM.id
                            WHERE ACP.partner_id = {partner_id}
                            AND ACP.create_date BETWEEN {date_from} AND {date_to}
                            AND ACP.payment_type = 'inbound'
                            AND ACM.state = 'posted';
                        ''')
        query_res = self._cr.fetchall()
        return query_res[0][0]

    @api.model
    def get_debts(self, **kwargs) -> Dict[str, Any]:
        partner_id = kwargs.get('partnerId')
        month_of_payment_period = kwargs.get('monthOfPaymentPeriod')
        year_of_payment_period = kwargs.get('yearOfPaymentPeriod')
        if not partner_id:
            raise ValidationError(_('The value of customer is required.'))
        elif not month_of_payment_period:
            raise ValidationError(_('The value of month is required.'))
        elif not year_of_payment_period:
            raise ValidationError(_('The value of year is required.'))
        is_leap_year = self.is_leap_year(int(year_of_payment_period))
        month = 31
        if int(month_of_payment_period) == 2:
            month = 29 if is_leap_year else 28
        elif int(month_of_payment_period) in [4, 6, 9, 11]:
            month = 30

        date_from = f"'{year_of_payment_period}-{month_of_payment_period}-01 00:00:00'"
        date_to = f"'{year_of_payment_period}-{month_of_payment_period}-{str(month)} 23:59:59'"

        money_total = self._get_sum_money_total_sale_orders(date_from, date_to, partner_id)
        if not money_total:
            raise UserError(_(f'Sale orders from {date_from} - {date_to} not found.'))
        paid_by_customer = self._get_sum_paid_money_payments(date_from, date_to, partner_id)
        if not paid_by_customer: paid_by_customer = 0.0
        incurred_customer_debts = money_total - paid_by_customer
        data = {
            'paid_by_customer': paid_by_customer,
            'money_total': money_total,
            'incurred_customer_debts': incurred_customer_debts,
            'payment_amount': incurred_customer_debts
        }
        return data

