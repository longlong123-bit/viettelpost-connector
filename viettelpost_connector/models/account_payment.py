import logging
import re
from odoo import fields, models, api, tools, _

_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError:
    _logger.warning("The num2words python library is not installed, amount-to-text features won't be fully available.")
    num2words = None


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    reason = fields.Text(string='Reason', required=True)
    prepared_by_id = fields.Many2one('res.users', string='Prepared by', required=True)
    object_receipt_payment = fields.Text(string='Receipt/Payment Object')
    voucher_sequence = fields.Char(string='Voucher', required=True)
    payment_category_id = fields.Many2one('payment.category', string='Category', required=True)

    payment_type = fields.Selection([
        ('outbound', 'Send'),
        ('inbound', 'Receive'),
    ], string='Payment Type', default='inbound', required=True, tracking=True)

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
    amount = fields.Monetary(currency_field='currency_id')

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