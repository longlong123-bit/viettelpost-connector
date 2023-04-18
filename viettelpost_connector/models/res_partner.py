import re

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import ustr


class PartnerVTPost(models.Model):
    _inherit = 'res.partner'
    _description = 'Configuration Address'

    vtp_province_id = fields.Many2one('viettelpost.province', string='Province')
    vtp_district_id = fields.Many2one('viettelpost.district', string='District')
    vtp_ward_id = fields.Many2one('viettelpost.ward', string='Ward')
    vtp_street = fields.Char(string='Street')
    vtp_address = fields.Char(string='Address')

    @api.onchange('vtp_ward_id')
    def _onchange_vtp_ward_id(self):
        for rec in self:
            if rec.vtp_ward_id:
                rec.vtp_district_id = rec.vtp_ward_id.district_id
                rec.vtp_province_id = rec.vtp_ward_id.district_id.province_id

    @staticmethod
    def format_address(text: str) -> str:
        return re.sub(r'^.*?\.', '', text).strip()

    @staticmethod
    def _handle_data_address(address: str) -> (dict, dict):
        dict_address: dict = dict(province='', district='', ward='', street='')
        address = re.sub(r"^\s+|\s+$|\n|\t", "", address)
        is_comma: bool = bool(re.search(r',', address, flags=re.I))
        new_address = address.split(',') if is_comma else address.split('-')
        new_address.reverse()
        new_address = [re.sub(r"^\s+|\s+$|\n|\t", "", item) for item in new_address]
        new_address = dict(zip(dict_address.keys(), new_address))
        return address, new_address

    def _get_province(self, province: str):
        if not province:
            raise ValidationError(_('Province unknown.'))
        province_format = self.format_address(province)
        province_id = self.env['viettelpost.province'].search([
            '|',
            ('province_name', 'ilike', f'%{province_format}%'),
            ('vtp_aliases', 'ilike', f'%{province_format}%')
        ], limit=1)
        return province_id.id

    def _get_district(self, district: str, province_id):
        if not district:
            raise ValidationError(_('District unknown.'))
        district_format = self.format_address(district)
        district_id = self.env['viettelpost.district'].search([
            '&',
            ('province_id', '=', province_id),
            '|',
            ('district_name', 'ilike', f'%{district_format.strip()}%'),
            ('vtp_aliases', 'ilike', f'%{district_format.strip()}%')
        ], limit=1)
        return district_id.id

    def _get_ward(self, ward: str, district_id):
        if not ward:
            raise ValidationError(_('Ward unknown.'))
        ward_format = self.format_address(ward)
        ward_id = self.env['viettelpost.ward'].search([
            '&',
            ('district_id', '=', district_id),
            '|',
            ('ward_name', 'ilike', f'%{ward_format.strip()}%'),
            ('vtp_aliases', 'ilike', f'%{ward_format.strip()}%')
        ], limit=1)
        return ward_id.id

    @staticmethod
    def _validate_case_import_with_street(value: dict):
        if 'vtp_province_id' not in value:
            raise ValidationError(_('The key province is missing.'))
        elif not value.get('vtp_province_id'):
            raise ValidationError(_('The value of province cannot be empty.'))
        elif 'vtp_district_id' not in value:
            raise ValidationError(_('The district is missing.'))
        elif not value.get('vtp_district_id'):
            raise ValidationError(_('The value of district cannot be empty.'))
        elif 'vtp_ward_id' not in value:
            ValidationError(_('The ward is missing.'))
        elif not value.get('vtp_ward_id'):
            raise ValidationError(_('The value of ward cannot be empty.'))
        elif not value.get('vtp_street'):
            raise ValidationError(_('The value of street cannot be empty.'))

    @staticmethod
    def _validate_case_import_with_address(value: dict):
        if not value.get('vtp_address', False):
            raise ValidationError(_('The value of address cannot be empty.'))

    def _get_name_import(self, value: dict) -> str:
        if 'name' in value:
            name = value.get('name', False)
            if not name:
                raise ValidationError(_('The value of name cannot be empty'))
        else:
            uid = self.env.uid
            user_id = self.env['res.users'].sudo().search([('id', '=', uid)])
            name = user_id.partner_id.name
        return name

    @staticmethod
    def _update_value(value: dict, name: str, province_id: int, district_id: int, ward_id: int, street: str, address: str):
        value.update({
            'name': name,
            'vtp_address': address,
            'vtp_province_id': province_id,
            'vtp_district_id': district_id,
            'vtp_ward_id': ward_id,
            'vtp_street': street,
            'type': 'delivery',
            'is_company': False,
            'email': value.get('email', False)
        })

    @api.model_create_multi
    def create(self, vals_list):
        try:
            if self.env.context.get('import_file', False):
                for value in vals_list:
                    if not self.env.context.get('has_headers'):
                        vals_list.remove(value)
                        self.env.context = dict(self.env.context)
                        self.env.context.update({'has_headers': True})
                        continue
                    name = self._get_name_import(value)
                    if 'vtp_address' in value:
                        self._validate_case_import_with_address(value)
                        old_address, address = self._handle_data_address(value.get('vtp_address'))
                        province_id = self._get_province(address.get('province'))
                        if not province_id: raise ValidationError(_(f'Province {address.get("province")} not found.'))
                        district_id = self._get_district(address.get('district'), province_id)
                        if not district_id: raise ValidationError(_(f'District {address.get("district")} not found.'))
                        ward_id = self._get_ward(address.get('ward'), district_id)
                        if not ward_id: raise ValidationError(_(f'Ward {address.get("ward")} not found.'))
                        self._update_value(value, name, province_id, district_id, ward_id, address.get('street'),
                                           old_address)
                    elif 'vtp_street' in value:
                        self._validate_case_import_with_street(value)
                        province_id = value.get('vtp_province_id')
                        district_id = value.get('vtp_district_id')
                        ward_id = value.get('vtp_ward_id')
                        street = value.get('vtp_street')
                        address = f'{street}, {ward_id}, {district_id}, {province_id}'
                        self._update_value(value, name, province_id, district_id, ward_id, street, address)
            result = super(PartnerVTPost, self).create(vals_list)
            return result
        except Exception as e:
            raise UserError(_(f'Import data failed. {ustr(e)}'))