from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError

class EmployeeManajemenTemplate(models.Model):
	_name = 'kpi.template.manajemen'
	_description = 'Template KPI Manajemen'
	_rec_name = 'ski'
	# _order = 'sequence'

	# sequence = fields.Integer(string='Sequence', )
	job_id = fields.Many2one(comodel_name='hr.job', string='HR Job')
	ski = fields.Char(string='Sasaran Kerja Individu')
	kpi = fields.Char(string='Key Performance Indicator')
	bobot = fields.Float(string='Bobot')
	target = fields.Float(string='Target')

class EmployeeManagementKpi(models.Model):
	_name = 'employee.manajemen.kpi'
	_inherit = ['mail.activity.mixin', 'mail.thread']
	_description = 'Employee Manajemen KPI'
	_check_company_auto = True
	
	kpi_manajemen_batch_id = fields.Many2one(comodel_name='kpi.manajemen.batch', string='KPI Manajemen Batch')
	name = fields.Char(string='Nomor')
	tgl_dibuat = fields.Date(string='Tanggal Dibuat', default=lambda self:fields.Date.context_today(self))
	periode_id = fields.Many2one(comodel_name='kpi.periode', string='Periode')
	month_ids = fields.Many2many(comodel_name='res.month', string='Month', related='periode_id.month_ids')
	tahun = fields.Char(string='Tahun')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Kabag', default=lambda s:s.env.user.employee_id.id)
	department_id = fields.Many2one(comodel_name='hr.department', string='Divisi/Bagian', related='employee_id.department_kelolaan_id')
	employee_parent_id = fields.Many2one(comodel_name='hr.employee', string='Kadiv', related='employee_id.parent_id')
	company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda s:s.env.company.id)
	state = fields.Selection(string='State', selection=[
		('draft', 'Draft'), 
		('in_progress', 'In Progress'),
		('approval_1', 'Approval 1'),
		# ('approval_2', 'Approval 2'),
		('done', 'Done'),
		('cancel', 'Cancel')], default='draft', copy=False, tracking=True)

	employee_kpi_count = fields.Integer(string='Count', compute='_compute_employee_kpi_count')
	employee_manajemen_kpi_line_ids = fields.One2many(comodel_name='employee.manajemen.kpi.line', inverse_name='employee_manajemen_kpi_id', string='Manajemen KPI Line')

	# CRUD METHOD (create, write, unlink)
	@api.model
	def create(self, vals):
		# CODE HERE
		vals['name'] = self.env['ir.sequence'].next_by_code('employee.manajemen.kpi.seq', fields.Date.to_date(vals.get('tgl_dibuat')))
		vals['tahun'] = fields.Date.to_date(vals.get('tgl_dibuat')).strftime("%Y")
		return super(EmployeeManagementKpi, self).create(vals)
	
	def unlink(self):
		for rec in self:
			if rec.state != 'cancel':
				raise ValidationError(_("Anda tidak dapat menghapus data, harap cancel terlebih dahulu."))
		super().unlink()

	
	# Logic Method	
	def _create_employee_manajemen(self):
		manajemen_batch_id = self.env['kpi.manajemen.batch']._find_manajemen_batch(self.periode_id, self.tahun, self.tgl_dibuat)
		self.kpi_manajemen_batch_id = manajemen_batch_id.id
		ski_values = []


		# values untuk KPI per karyawan
		employee_kpi_line_values = [{
				'employee_manajemen_kpi_id' : self.id,
				'kpi_manajemen_batch_id' : manajemen_batch_id.id,
				'employee_id' : employee.id,
				'job_title_id' : employee.job_title_id.id,
				'detail_ids' : employee.job_id._prepare_ski_values(employee)
			} for employee in self.employee_id.child_ids]

		employee_kpi_line_ids = self.env['employee.manajemen.kpi.line'].create(employee_kpi_line_values)
		employee_kpi_line_ids.write({
			'kpi_manajemen_batch_id' : manajemen_batch_id.id,
			'employee_manajemen_kpi_id' : self.id,

		})
		return employee_kpi_line_ids
	
	def _compute_employee_kpi_count(self):
		for rec in self:
			rec.employee_kpi_count = len(rec.employee_manajemen_kpi_line_ids)

	# Button Method
	def button_submit(self):
		employee_kpi_line_ids = self._create_employee_manajemen()
		return self.write({'state' : 'in_progress'})

	def button_cancel(self):
		return self.write({'state' : 'cancel'})
 
	# Action Method
	def action_show_ski(self):
		self.ensure_one()
		tree_view = self.env.ref('mum_kpi.employee_manajemen_kpi_line_view_tree')
		form_view = self.env.ref('mum_kpi.employee_manajemen_kpi_line_view_form')
		# pivot_view = self.env.ref('mum_kpi.employee_kpi_view_pivot')
		return {
			'name': _('SKI Karyawan '),
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'employee.manajemen.kpi.line',
			'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
			'view_id': tree_view.id,
			'target': 'self',
			'domain' : [('id', 'in', self.employee_manajemen_kpi_line_ids.ids)]
		}

class EmployeeManajemenKpiLine(models.Model):
	# Class untuk Hasil perhitungan KPI Per Karyawan
	_name = 'employee.manajemen.kpi.line'
	_description = 'Emplyoee Manajemen KPI Line'
	_rec_name = 'employee_id'

	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan', index=True)
	employee_job_id = fields.Many2one(comodel_name='hr.job', string='Posisi', related='employee_id.job_id', store=True)
	job_title_id = fields.Many2one(comodel_name='job.title', string='Job Title')
	service_quality_id = fields.Many2one(comodel_name='kpi.service.quality', string='Service Excelent')
	employee_parent_id = fields.Many2one(comodel_name='hr.employee', string='Manajer', related='employee_id.parent_id')
	employee_manajemen_kpi_id = fields.Many2one(comodel_name='employee.manajemen.kpi', string='KPI Manajemen')
	kpi_manajemen_batch_id = fields.Many2one(comodel_name='kpi.manajemen.batch', string='KPI Manajemen Batch')
	total_bobot = fields.Float(string='Total Bobot', compute='_compute_bobot_pencapaian')
	state = fields.Selection(string='State', related='employee_manajemen_kpi_id.state')
	absen_value = fields.Float(string='Absensi (Rp)')
	nilai_pencapaian = fields.Float(string='Nilai Pencapaian', compute='_compute_bobot_pencapaian')
	service_value = fields.Float(string='Service (Rp)')
	absen = fields.Float(string='Absensi')
	total_pencapaian = fields.Float(string='Total Pencapaian', compute='_compute_bobot_pencapaian')
	komite = fields.Float(string='Komite (Rp)')

	detail_ids = fields.One2many(comodel_name='employee.manajemen.kpi.line.detail', inverse_name='employee_manajemen_kpi_line_id', string='Details')

	def action_show_details(self):
		self.ensure_one()
		view = self.env.ref('mum_kpi.employee_manajemen_kpi_line_view_form')
		return {
			'name': _('Detail KPI Karyawan %s'%self.employee_id.name),
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': self._name,
			'views': [(view.id, 'form')],
			'view_id': view.id,
			'target': 'self',
			'res_id': self.id,
		}
	
	def _compute_bobot_pencapaian(self):
		for rec in self:
			rec.total_bobot = sum(x.bobot for x in rec.detail_ids)
			rec.nilai_pencapaian = sum(x.nilai_pencapaian for x in rec.detail_ids)
			rec.total_pencapaian = rec.nilai_pencapaian + rec.absen

class EmployeeManajemenKpiLineDetails(models.Model):
	# Class untuk mengisi detail Sasaran Kerja Individu
	_name = 'employee.manajemen.kpi.line.detail'
	_description = 'Employee Manajemen KPI Line Details'
	_rec_name = 'employee_id'

	employee_manajemen_kpi_line_id = fields.Many2one(comodel_name='employee.manajemen.kpi.line', string='KPI Manajemen Karyawan')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan', index=True)
	employee_parent_id = fields.Many2one(comodel_name='hr.employee', string='Manajer', related='employee_id.parent_id')
	employee_job_id = fields.Many2one(comodel_name='hr.job', string='Posisi', related='employee_id.job_id', store=True)
	employee_manajemen_kpi_id = fields.Many2one(comodel_name='employee.manajemen.kpi', string='KPI Manajemen')
	kpi_manajemen_batch_id = fields.Many2one(comodel_name='kpi.manajemen.batch', string='KPI Manajemen Batch')
	state = fields.Selection(string='State', related='employee_manajemen_kpi_id.state')
	
	job_id = fields.Many2one(comodel_name='hr.job', string='HR Job')
	ski = fields.Char(string='Sasaran Kerja Individu')
	kpi = fields.Char(string='Key Performance Indicator')
	bobot = fields.Float(string='Bobot')
	target = fields.Float(string='Target')
	realisasi = fields.Float(string='Realisasi')
	pencapaian = fields.Float(string='Pencapaian', compute='_compute_pencapaian')
	nilai_pencapaian = fields.Float(string='Nilai Pencapaian', compute='_compute_pencapaian')
	

	@api.depends('bobot', 'target', 'realisasi')
	def _compute_pencapaian(self):
		for rec in self:
			rec.pencapaian = rec.target and rec.realisasi / rec.target or 0
			rec.nilai_pencapaian = rec.pencapaian * rec.bobot



