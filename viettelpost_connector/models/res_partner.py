from odoo import fields, models, api


class PartnerVTPost(models.Model):
    _inherit = 'res.partner'
    _description = 'Configuration Address'

    vtp_province_id = fields.Many2one('viettelpost.province', string='Province')
    vtp_district_id = fields.Many2one('viettelpost.district', string='District')
    vtp_ward_id = fields.Many2one('viettelpost.ward', string='Ward')
    vtp_street = fields.Char(string='Street')

    @api.onchange('vtp_ward_id')
    def _onchange_vtp_ward_id(self):
        for rec in self:
            if rec.vtp_ward_id:
                rec.vtp_district_id = rec.vtp_ward_id.district_id
                rec.vtp_province_id = rec.vtp_ward_id.district_id.province_id
