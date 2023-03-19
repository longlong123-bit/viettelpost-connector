from odoo import fields, models


class DebsReportWizard(models.TransientModel):
    _name = 'debs.report.wizard'
    _description = 'Used for debs customer report'

    date_from = fields.Date(string='Date from', required=True)
    date_to = fields.Date(string='Date to', required=True)
    partner_ids = fields.Many2many('res.partner', string='Customer', required=True)

    def action_print_debs_report(self):
        ...
