from odoo import fields, models


class PaymentCategory(models.Model):
    _name = 'payment.category'
    _description = 'The category of payment. Used for register payment'

    name = fields.Char(string='Name', required=True)
    category = fields.Char(string='Code', required=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "The name category already exists!")
    ]