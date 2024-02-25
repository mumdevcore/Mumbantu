# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, Command, _

class EmployeePublic(models.Model):
	_inherit = 'hr.employee.public'

	inisial = fields.Char(string='Inisial', related='employee_id.inisial', compute_sudo=True)
	email_pribadi = fields.Char(string='Email Pribadi', related='employee_id.email_pribadi', compute_sudo=True)
	nomor_wa = fields.Char(string='No WA', related='employee_id.nomor_wa', compute_sudo=True)
	inisial_jabatan = fields.Char(string='Inisial Jabatan', related='job_id.inisial',)
	kota_id = fields.Many2one('vit.kota',string='Kota/Kabupaten', related='employee_id.kota_id')

	hr_certification_line = fields.One2many('hr.certification', 'employee_id', string='HR Employee Certification',)