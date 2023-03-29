from datetime import datetime
import re
from typing import Optional, Dict, Any, List, Tuple, NoReturn
from datetime import date
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class AccountPaymentWizard(models.TransientModel):
    _name = 'account.payment.wizard'
    _description = 'Register payment'
    _rec_name = 'voucher_sequence'

    MONTH_SELECTION: List[Tuple] = [
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

    @staticmethod
    def get_years():
        now = datetime.now()
        year_list = [(i, f'{i}') for i in range(now.year - 2, now.year + 2)]
        return year_list

    @api.model
    def action_register_payment(self):
        action = self.env.ref('account_payment_extension.register_payment_wizard_action').read()[0]
        return action

    date_voucher = fields.Date(string='Date Voucher', default=lambda self: date.today(), required=True)
    partner_id = fields.Many2one('res.partner', 'Object/Customer', required=True)
    partner_address = fields.Char(related='partner_id.vtp_address', string='Address')
    prepared_by_id = fields.Many2one('res.users', string='Prepared by', required=True, default=lambda self: self.env.uid)
    reason = fields.Text(string='Reason', required=True)
    object_receipt_payment = fields.Text(string='Receipt/Payment Object')
    month_of_payment_period = fields.Selection(MONTH_SELECTION, default='01')
    year_of_payment_period = fields.Selection(selection=lambda self: AccountPaymentWizard.get_years())
    payment_amount = fields.Monetary(string='Amount', currency_field='currency_id')
    payment_type = fields.Selection([
        ('outbound', 'Send'),
        ('inbound', 'Receive'),
    ], string='Payment Type', default='inbound', required=True)

    def _get_sequence_receipt_bank(self):
        sequence = self.env['ir.sequence'].search([
            ('code', '=', 'account.payment'),
            ('prefix', '=', 'PT'),
            ('name', '=', 'Receipt Bank Sequence'),
            ('active', '=', True)
        ])
        return sequence

    def _get_sequence_receipt_cash(self):
        sequence = self.env['ir.sequence'].search([
            ('code', '=', 'account.payment'),
            ('prefix', '=', 'PT'),
            ('name', '=', 'Receipt Cash Sequence'),
            ('active', '=', True)
        ])
        return sequence

    def _get_sequence_payment_bank(self):
        sequence = self.env['ir.sequence'].search([
            ('code', '=', 'account.payment'),
            ('prefix', '=', 'PC'),
            ('name', '=', 'Payment Bank Sequence'),
            ('active', '=', True)
        ])
        return sequence

    def _get_sequence_payment_cash(self):
        sequence = self.env['ir.sequence'].search([
            ('code', '=', 'account.payment'),
            ('prefix', '=', 'PC'),
            ('name', '=', 'Payment Cash Sequence'),
            ('active', '=', True)
        ])
        return sequence

    def _get_onchange_sequence(self):
        if self.payment_type == 'inbound' and self.journal_id.type == 'bank':
            sequence = self._get_sequence_receipt_bank()
        elif self.payment_type == 'inbound' and self.journal_id.type == 'cash':
            sequence = self._get_sequence_receipt_cash()
        elif self.payment_type == 'outbound' and self.journal_id.type == 'bank':
            sequence = self._get_sequence_payment_bank()
        elif self.payment_type == 'outbound' and self.journal_id.type == 'cash':
            sequence = self._get_sequence_payment_cash()
        else:
            raise UserError(_('Do not find sequence.'))
        next_document = sequence.get_next_char(sequence.number_next_actual)
        self._cr.execute('''SELECT voucher_sequence FROM account_payment''')
        query_res = self._cr.fetchall()
        while next_document in [res[0] for res in query_res]:
            next_tmp = self.env['ir.sequence'].next_by_code('account.payment')
            next_document = next_tmp
        return next_document

    def _get_default_sequence_base(self):
        sequence = self._get_sequence_receipt_bank()
        next_document = sequence.get_next_char(sequence.number_next_actual)
        self._cr.execute('''SELECT voucher_sequence FROM account_payment''')
        query_res = self._cr.fetchall()
        while next_document in [res[0] for res in query_res]:
            next_tmp = self.env['ir.sequence'].next_by_code('account.payment')
            next_document = next_tmp
        return next_document

    def _get_default_journal(self) -> int:
        bank_id = self.env['account.journal'].search([('type', '=', 'bank')])
        return bank_id.id

    voucher_sequence = fields.Char(string='Voucher', required=True, default=_get_default_sequence_base)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, default=_get_default_journal)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    debts = fields.Monetary(string='Debts', currency_field='currency_id', readonly=True)
    paid = fields.Monetary(string='Paid', currency_field='currency_id', readonly=True)
    arise = fields.Monetary(string='Arise', currency_field='currency_id', readonly=True)
    payment_category_id = fields.Many2one('payment.category', string='Category', required=True)
    payment_method_line_id = fields.Many2one('account.payment.method.line', string='Payment Method',
                                             readonly=False, store=True, copy=False,
                                             compute='_compute_payment_method_line_id',
                                             domain="[('id', 'in', available_payment_method_line_ids)]")
    available_payment_method_line_ids = fields.Many2many('account.payment.method.line',
                                                         compute='_compute_payment_method_line_fields')
    hide_payment_method_line = fields.Boolean(compute='_compute_payment_method_line_fields')

    @api.onchange('payment_type', 'journal_id')
    def _onchange_payment_type_and_journal_id(self):
        for rec in self:
            domain = dict()
            if rec.payment_type or rec.journal_id:
                rec.voucher_sequence = self._get_onchange_sequence()
                if rec.payment_type == 'inbound':
                    domain = {'payment_category_id': [('category', '=', 'receipt')]}
                else:
                    domain = {'payment_category_id': [('category', '=', 'payment')]}
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

    def _get_payment_method_codes_to_exclude(self) -> List:
        self.ensure_one()
        return []

    @api.onchange('month_of_payment_period', 'year_of_payment_period')
    def _onchange_validated_year(self):
        for rec in self:
            if rec.year_of_payment_period and rec.month_of_payment_period:
                rec.get_debts()

    def _prepare_data_payment_vals_from_wizard(self) -> Dict[str, Any]:
        payment_vals: Dict[str, Any] = {
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
        if self.debts == self.payment_amount and self.payment_amount > 0:
            lst_so_ids = self._get_lst_ids_sale_order(self.partner_id.id, self.month_of_payment_period, self.year_of_payment_period)
            lst_browse_so_ids = self.env['sale.order'].browse(lst_so_ids)
            for so in lst_browse_so_ids:
                so.action_done()
        if self.env.context.get('is_print'):
            return self.env.ref('account_payment_extension.action_report_payment_receipt').sudo().report_action(account_payment)
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
        is_leap_year = True if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0 else False
        return is_leap_year

    def _get_lst_ids_sale_order(self, partner_id: int, month: str, year: int):
        is_leap_year: bool = self.is_leap_year(int(year))
        day_of_month: int = 31
        if int(month) == 2:
            day_of_month = 29 if is_leap_year else 28
        elif int(self) in [4, 6, 9, 11]:
            day_of_month = 30

        date_from: str = f"'{year}-{month}-01 00:00:00'"
        date_to: str = f"'{year}-{month}-{str(day_of_month)} 23:59:59'"
        self._cr.execute(f'''
                            SELECT id FROM sale_order 
                            WHERE partner_id = {partner_id}
                            AND state = 'sale'
                            AND date_order BETWEEN {date_from} AND {date_to};
                        ''')
        query_res = self._cr.fetchall()
        formatted_res = [item[0] for item in query_res]
        return formatted_res

    def _get_sum_money_total_sale_orders(self, date_from: str, date_to: str, partner_id: int) -> Optional[float]:
        self._cr.execute(f'''
                            SELECT SUM(COALESCE(money_total, 0)) FROM sale_order 
                            WHERE partner_id = {partner_id}
                            AND state = 'sale'
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

    def get_debts(self):
        if not self.partner_id:
            raise ValidationError(_('The value of customer is required.'))
        elif not self.month_of_payment_period:
            raise ValidationError(_('The value of month is required.'))
        elif not self.year_of_payment_period:
            raise ValidationError(_('The value of year is required.'))
        is_leap_year: bool = self.is_leap_year(int(self.year_of_payment_period))
        month: int = 31
        if int(self.month_of_payment_period) == 2:
            month = 29 if is_leap_year else 28
        elif int(self.month_of_payment_period) in [4, 6, 9, 11]:
            month = 30

        date_from: str = f"'{self.year_of_payment_period}-{self.month_of_payment_period}-01 00:00:00'"
        date_to: str = f"'{self.year_of_payment_period}-{self.month_of_payment_period}-{str(month)} 23:59:59'"

        arise: float = self._get_sum_money_total_sale_orders(date_from, date_to, self.partner_id.id)
        if not arise:
            raise UserError(f'Khách hàng {self.partner_id.name} không có công nợ trong tháng {self.month_of_payment_period}/{self.year_of_payment_period}')
        paid: float = self._get_sum_paid_money_payments(date_from, date_to, self.partner_id.id)
        if not paid: paid = 0.0
        self.paid = paid
        self.arise = arise
        self.debts = arise - paid
        self.payment_amount = self.debts
