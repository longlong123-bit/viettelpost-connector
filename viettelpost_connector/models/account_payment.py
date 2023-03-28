import logging
import re
from typing import List, Tuple, Optional
from datetime import datetime
from odoo import fields, models, api, tools, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError:
    _logger.warning("The num2words python library is not installed, amount-to-text features won't be fully available.")
    num2words = None


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _rec_name = 'voucher_sequence'
    _order = 'voucher_sequence desc'

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

    month_of_payment_period = fields.Selection(MONTH_SELECTION, default='01')
    year_of_payment_period = fields.Selection(selection=lambda self: AccountPayment.get_years())
    debts = fields.Monetary(string='Debts', currency_field='currency_id', readonly=True)
    paid = fields.Monetary(string='Paid', currency_field='currency_id', readonly=True)
    arise = fields.Monetary(string='Arise', currency_field='currency_id', readonly=True)
    reason = fields.Text(string='Reason', required=True)
    prepared_by_id = fields.Many2one('res.users', string='Prepared by', required=True, default=lambda self: self.env.uid)
    object_receipt_payment = fields.Text(string='Receipt/Payment Object')
    voucher_sequence = fields.Char(string='Voucher', required=True, default=_get_default_sequence_base)
    payment_category_id = fields.Many2one('payment.category', string='Category', required=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer/Vendor",
        required=True,
        store=True, readonly=False, ondelete='restrict',
        domain="['|', ('parent_id','=', False), ('is_company','=', True)]",
        tracking=True,
        check_company=True)
    partner_address = fields.Char(related='partner_id.vtp_address', string='Address')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    def action_create_and_print(self):
        if self.env.context.get('is_print'):
            return self.env.ref('viettelpost_connector.action_report_payment_receipt').sudo().report_action(self)

    @api.model
    def action_register_payment(self):
        action = self.env.ref('viettelpost_connector.register_payment_wizard_action').read()[0]
        return action

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(AccountPayment, self).fields_view_get(view_id, view_type, toolbar, submenu)
        report_id = self.env.ref('account.action_report_payment_receipt').id
        if view_type == 'form' and report_id and toolbar and result['toolbar'] and result['toolbar'].get('print'):
            remove_report = [rec for rec in result['toolbar'].get('print') if rec.get('id') == report_id]
            if remove_report and remove_report[0]:
                result['toolbar'].get('print').remove(remove_report[0])
        elif view_type == 'tree' and report_id and toolbar and result['toolbar'] and result['toolbar'].get('print'):
            remove_report = [rec for rec in result['toolbar'].get('print') if rec.get('id') == report_id]
            if remove_report and remove_report[0]:
                result['toolbar'].get('print').remove(remove_report[0])
        return result

    def _get_name_payment_voucher(self):
        self.ensure_one()
        receipt = u'Phiếu thu'
        payment = u'Phiếu chi'
        name = f'{receipt} {self.voucher_sequence}' if self.payment_type == 'inbound' else f'{payment} {self.voucher_sequence}'
        return name

    def _amount_to_words(self, amount):
        self.ensure_one()

        def _num2words(number, lang):
            try:
                return num2words(number, lang=lang).capitalize()
            except NotImplementedError:
                return num2words(number, lang='en').title()
        if num2words is None:
            logging.getLogger(__name__).warning("The library 'num2words' is missing, cannot render textual amounts.")
            return ""
        formatted = "%.{0}f".format(self.currency_id.decimal_places) % amount
        parts = formatted.partition('.')
        integer_value = int(parts[0])
        fractional_value = int(parts[2] or 0)

        lang = tools.get_lang(self.env)
        lang.iso_code = 'vi_VN'
        amount_words = tools.ustr('{amt_value} {amt_word}').format(
            amt_value=_num2words(integer_value, lang=lang.iso_code),
            amt_word=self.currency_id.currency_unit_label,
        )
        if not self.currency_id.is_zero(amount - integer_value):
            amount_words += ' ' + _('and') + tools.ustr(' {amt_value} {amt_word}').format(
                amt_value=_num2words(fractional_value, lang=lang.iso_code),
                amt_word=self.currency_id.currency_subunit_label
            )
        amount_words = re.sub(r"\bDong\b", "đồng", amount_words, flags=re.I)
        return amount_words

    @api.depends('amount')
    def _compute_amount_to_words(self):
        for rec in self:
            rec.amount_to_words = rec._amount_to_words(rec.amount)

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
        self.amount = self.debts

    @api.onchange('month_of_payment_period', 'year_of_payment_period')
    def _onchange_validated_year(self):
        for rec in self:
            if rec.year_of_payment_period and rec.month_of_payment_period:
                rec.get_debts()
