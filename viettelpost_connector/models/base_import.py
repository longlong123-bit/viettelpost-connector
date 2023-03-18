from odoo import models


class BaseImportInherit(models.TransientModel):
    _inherit = 'base_import.import'

    def execute_import(self, fields, columns, options, dryrun=False):
        res = super(BaseImportInherit, self.with_context(has_headers=options.get('has_headers'))).execute_import(fields, columns, options, dryrun=False)
        return res