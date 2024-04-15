# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, Command, _

class Employee(models.Model):
	_inherit = 'hr.employee'

	hr_certification_line = fields.One2many('hr.certification', 'employee_id', string='HR Employee Certification',)

	inisial = fields.Char(string='Inisial',)
	email_pribadi = fields.Char(string='Email Pribadi',)
	nomor_wa = fields.Char(string='No WA',)
	inisial_jabatan = fields.Char(string='Inisial Jabatan', related='job_id.inisial')
	cabang_id = fields.Many2one('res.cabang',string='Cabang',)
	kota_id = fields.Many2one('vit.kota',string='Kota/Kabupaten', related='cabang_id.kota_id', store=True, precompute=True)
	contract_type_id = fields.Many2one('hr.contract.type', string='Status Karyawan',)
	job_title_id = fields.Many2one('job.title',string='Title',)


	jenis_kelamin = fields.Selection([('pria', 'Pria'), ('wanita', 'Wanita')], string='Jenis Kelamin', copy=False, groups="hr.group_hr_user")
	tgl_bergabung = fields.Date(string='Tgl Bergabung', groups="hr.group_hr_user")
	tgl_resign = fields.Date(string='Tgl Resign', groups="hr.group_hr_user")
	agama_id = fields.Many2one('res.agama',string='Agama', groups="hr.group_hr_user")
	no_bpjstk = fields.Char(string='No BPJSTK', groups="hr.group_hr_user")
	no_bpjs_kesehatan = fields.Char(string='No BPJS Kesehatan', groups="hr.group_hr_user")
	no_asuransi = fields.Char(string='No Asuransi', groups="hr.group_hr_user")
	nama_ibu = fields.Char(string='Nama Ibu', groups="hr.group_hr_user")
	no_npwp = fields.Char(string='No NPWP', groups="hr.group_hr_user")
	status_pajak_id = fields.Many2one('status.pajak',string='Status Pajak', groups="hr.group_hr_user")
	
	def name_get(self):
		result = []
		for employee in self:
			name = employee.name
			if employee._context.get('show_inisial'):
				name = employee.inisial
			result.append((employee.id, name))
			# print(name)
		return result