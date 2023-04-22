import hashlib
import os
from odoo import fields, models, api


def nonce(length=80, prefix="odoo"):
    rbytes = os.urandom(length)
    return "{}_{}".format(prefix, str(hashlib.sha1(rbytes).hexdigest()))


class PartnerVTPost(models.Model):
    _inherit = 'res.partner'
    _description = 'Configuration Address'

    vtp_province_id = fields.Many2one('viettelpost.province', string='Province')
    vtp_district_id = fields.Many2one('viettelpost.district', string='District')
    vtp_ward_id = fields.Many2one('viettelpost.ward', string='Ward')
    vtp_street = fields.Char(string='Street')

    token = fields.Char(string='Token', help='Authorization of delivery carrier', tracking=True)
    type = fields.Selection(selection_add=[('webhook_service', 'Webhook Service')])

    def get_access_token(self):
        self.write({'token': nonce()})

    @api.onchange('vtp_ward_id')
    def _onchange_vtp_ward_id(self):
        for rec in self:
            if rec.vtp_ward_id:
                rec.vtp_district_id = rec.vtp_ward_id.district_id
                rec.vtp_province_id = rec.vtp_ward_id.district_id.province_id
