from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError
import random

class EmployeeKpiBatch(models.AbstractModel):
	_name = 'employee.kpi.batch'
	
	periode_id = fields.Many2one(comodel_name='kpi.periode', string='Periode')
	tahun = fields.Char(string='Tahun')
	tgl_dibuat = fields.Date(string='Tgl Dibuat')


class KpiMekaarBatch(models.Model):
	_name = 'kpi.mekaar.batch'
	_inherit = 'employee.kpi.batch'

	name = fields.Char(string='Nomor Batch')

	jml_ro = fields.Integer(string='Jml RO', compute='_compute_line')
	jml_alw = fields.Integer(string='Jml ALW', compute='_compute_line')
	jml_kro = fields.Integer(string='Jml KRO', compute='_compute_line')
	total_ro = fields.Integer(string='RO Terdaftar')
	total_alw = fields.Integer(string='ALW Terdaftar')
	total_kro = fields.Integer(string='KRO Terdaftar')
	
	
	employee_ro_kpi_line = fields.One2many(comodel_name='employee.ro.kpi', inverse_name='kpi_mekaar_batch_id', string='KPI RO', domain=[('state', 'in', ('approval_2', 'done'))])
	employee_alw_kpi_line = fields.One2many(comodel_name='employee.alw.kpi', inverse_name='kpi_mekaar_batch_id', string='KPI ALW', domain=[('state', 'in', ('approval_2', 'done'))])
	employee_kro_kpi_line = fields.One2many(comodel_name='employee.kro.kpi', inverse_name='kpi_mekaar_batch_id', string='KPI KRO', domain=[('state', 'in', ('approval_2', 'done'))])
	kpi_resume_grading_ro_line = fields.One2many(comodel_name='resume.kpi.grading', inverse_name='kpi_mekaar_batch_id', string='Resume Grading RO')
	kpi_resume_grading_alw_line = fields.One2many(comodel_name='resume.kpi.grading', inverse_name='kpi_mekaar_batch_id', string='Resume Grading ALW')
	total_insentif_kro = fields.Float(string='Insentif KRO', compute='_compute_total_insentif')
	total_insentif_ro = fields.Float(string='Insentif RO', compute='_compute_total_insentif')
	total_insentif_alw = fields.Float(string='Insentif ALW', compute='_compute_total_insentif')
	total_insentif = fields.Float(string='Total Insentif', compute='_compute_total_insentif')
	total_penyesuaian_insentif_kro = fields.Float(string='Penyesuaian KRO', compute='_compute_total_insentif')
	total_penyesuaian_insentif_ro = fields.Float(string='Penyesuaian RO', compute='_compute_total_insentif')
	total_penyesuaian_insentif_alw = fields.Float(string='Penyesuaian ALW', compute='_compute_total_insentif')
	total_penyesuaian_insentif = fields.Float(string='Total Penyesuaian', compute='_compute_total_insentif')
	state = fields.Selection(string='State', selection=[('draft', 'Draft'), ('done', 'Disetujui'), ('cancel', 'Cancel')], default='draft', copy='false', tracking=True)

	# def unlink(self):
	# 	for rec in self:
	# 		raise ValidationError(_("Dokumen tidak dapat dihapus."))

	@api.model
	def create(self, vals):
		params = self.env['ir.config_parameter'].sudo()
		if not vals.get('tgl_dibuat'):
			raise ValidationError(_("Kolom Tgl Dibuat tidak boleh kosong."))
		vals['name'] = self.env['ir.sequence'].next_by_code('kpi.mekaar.batch.seq', fields.Date.to_date(vals.get('tgl_dibuat')))
		vals['tahun'] = fields.Date.to_date(vals.get('tgl_dibuat')).strftime("%Y")

		ro_id = int(params.get_param('mum_kpi.default_job_ro_id'))
		alw_id = int(params.get_param('mum_kpi.default_job_alw_id'))
		kro_id = int(params.get_param('mum_kpi.default_job_kro_id'))
		vals['total_ro'] = self.env['hr.employee'].search_count([('job_id', '=', ro_id)])
		vals['total_alw'] = self.env['hr.employee'].search_count([('job_id', '=', alw_id)])
		vals['total_kro'] = self.env['hr.employee'].search_count([('job_id', '=', kro_id)])
		return super().create(vals)
	
	def _compute_line(self):
		for rec in self:
			rec.jml_ro = len(rec.employee_ro_kpi_line)
			rec.jml_alw = len(rec.employee_alw_kpi_line)
			rec.jml_kro = len(rec.employee_kro_kpi_line)


	@api.depends(
		'employee_kro_kpi_line.total_insentif',
		'employee_ro_kpi_line.total_insentif',
		'employee_alw_kpi_line.total_insentif',
		'employee_kro_kpi_line.penyesuaian',
		'employee_ro_kpi_line.penyesuaian',
		'employee_alw_kpi_line.penyesuaian',
	)
	def _compute_total_insentif(self):
		for rec in self:
			rec.total_insentif_kro = sum(line.total_insentif for line in rec.employee_ro_kpi_line)
			rec.total_insentif_ro = sum(line.total_insentif for line in rec.employee_alw_kpi_line)
			rec.total_insentif_alw = sum(line.total_insentif for line in rec.employee_kro_kpi_line)
			rec.total_insentif = rec.total_insentif_kro + rec.total_insentif_ro + rec.total_insentif_alw

			rec.total_penyesuaian_insentif_kro = sum(line.penyesuaian for line in rec.employee_ro_kpi_line)
			rec.total_penyesuaian_insentif_ro = sum(line.penyesuaian for line in rec.employee_alw_kpi_line)
			rec.total_penyesuaian_insentif_alw = sum(line.penyesuaian for line in rec.employee_kro_kpi_line)
			rec.total_penyesuaian_insentif = rec.total_penyesuaian_insentif_kro + rec.total_penyesuaian_insentif_ro + rec.total_penyesuaian_insentif_alw
			

	def button_approve(self):
		self.employee_kro_kpi_line.write({'state' : 'done'})
		self.write({'state' : 'done'})

	def button_draft(self):
		self.write({'state' : 'draft'})

	def _find_mekaar_batch(self, periode_id, tahun, tgl_dibuat):
		mekaar_batch_id = self.sudo().search([('periode_id', '=', periode_id.id), ('tahun', '=', tahun)])
		if not mekaar_batch_id:
			mekaar_batch_id = self.sudo().create({'periode_id' : periode_id.id, 'tahun' : tahun, 'tgl_dibuat' : tgl_dibuat})
		
		return mekaar_batch_id