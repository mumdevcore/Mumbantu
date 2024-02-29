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
	jenis_kelamin = fields.Selection([('pria', 'Pria'), ('wanita', 'Wanita')], string='Jenis Kelamin', copy=False)
	# kota_kabupaten
	tgl_bergabung = fields.Date(string='Tgl Bergabung')
	tgl_resign = fields.Date(string='Tgl Resign')
	agama_id = fields.Many2one('res.agama',string='Agama',)
	no_bpjstk = fields.Char(string='No BPJSTK',)
	no_bpjs_kesehatan = fields.Char(string='No BPJS Kesehatan',)
	no_asuransi = fields.Char(string='No Asuransi',)
	nama_ibu = fields.Char(string='Nama Ibu',)
	no_npwp = fields.Char(string='No NPWP',)
	status_pajak_id = fields.Many2one('status.pajak',string='Status Pajak',)
	job_title_id = fields.Many2one('job.title',string='Title',)
	cabang_id = fields.Many2one('res.cabang',string='Cabang',)
	kota_id = fields.Many2one('vit.kota',string='Kota/Kabupaten', related='cabang_id.kota_id', store=True, precompute=True)
	contract_type_id = fields.Many2one('hr.contract.type', string='Status Karyawan',)