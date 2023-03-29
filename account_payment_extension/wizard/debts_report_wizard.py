from typing import Dict, Any
from odoo import fields, models


class DebtsReportWizard(models.TransientModel):
    _name = 'debts.report.wizard'
    _description = 'Used for debts customer report'

    date_from = fields.Date(string='Date from', required=True)
    date_to = fields.Date(string='Date to', required=True)
    partner_ids = fields.Many2many('res.partner', string='Customer', required=True)

    def _get_name_report_xls(self):
        name = f'DS tổng hợp công nợ {self.date_from.year}+{self.date_to.year}' if self.date_from.year != self.date_to.year else f'DS tổng hợp công nợ {self.date_from.year}'
        return name

    def action_print_debts_report(self):
        data: Dict[str, Any] = {
            'lst_partner_ids': [partner.id for partner in self.partner_ids],
            'date_start': self.date_from,
            'date_end': self.date_to,
        }
        return self.env.ref('account_payment_extension.action_debts_report').report_action(self, data=data)
