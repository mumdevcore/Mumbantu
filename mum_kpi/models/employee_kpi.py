from odoo import _, api, fields, models, Command


class EmployeeKpiBatch(models.Model):
	_name = 'employee.kpi.batch'
	_inherit = ['mail.activity.mixin', 'mail.thread']
	_description = 'Insentif RO'
	_check_company_auto = True

	name = fields.Char(string='Name')
	tgl_dibuat = fields.Date(string='Tanggal Dibuat', default=lambda self:fields.Date.context_today(self))
	tahun = fields.Char(string='Tahun')
	periode_id = fields.Many2one(comodel_name='kpi.periode', string='Periode Insentif')
	month_ids = fields.Many2many(comodel_name='res.month', string='Bulan')
	kro_id = fields.Many2one(comodel_name='hr.employee', string='KRO', default=lambda s:s.env.user.employee_id)
	state = fields.Selection(string='State', selection=[
		('draft', 'Draft'), 
		('in_progress', 'In Progress'),
		('submit', 'Submit'),
		('approval_1', 'Approval 1'),
		('approval_2', 'Approval 2'),
		('done', 'Done'),
		('cancel', 'Cancel')], default='draft', copy=False, tracking=True)
	company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda self:self.env.company)
	user_approval_1 = fields.Many2one(comodel_name='res.users', string='User Approval 1')
	user_approval_2 = fields.Many2one(comodel_name='res.users', string='User Approval 2')
	show_approval_button = fields.Boolean(default=False, compute='_compute_show_approval_button')
	employee_kpi_line = fields.One2many(comodel_name='employee.kpi', inverse_name='employee_kpi_batch_id', string='Employees KPI')
	employee_monthly_kpi_line = fields.One2many(comodel_name='employee.monthly.kpi.line', inverse_name='employee_kpi_batch_id', string='Employees Monthly KPI Line')

	@api.model
	def create(self, vals):
		# CODE HERE
		vals['name'] = self.env['ir.sequence'].next_by_code('employee.kpi.batch.seq', fields.Date.to_date(vals.get('tgl_dibuat')))
		return super(EmployeeKpiBatch, self).create(vals)
	
	@api.onchange('kro_id')
	def _onchange_kro_id(self):
		self.user_approval_1 = self.kro_id.parent_id.user_id.id
		self.user_approval_2 = self.user_approval_1.parent_id.user_id.id
	
	@api.onchange('periode_id')
	def _onchange_periode(self):
		self.month_ids = self.periode_id.month_ids
	
	def _create_employee_kpi(self):
		employee_ids = self.kro_id.child_ids
		
		# values utk data penilaian bulanan per karyawan
		monthly_kpi_line_values = [(Command.create({
			'name' : f'{month.name} {self.tgl_dibuat.strftime("%Y")}',
			'month_id' : month.id,
		})) for month in self.month_ids]
		
		# values untuk KPI per karyawan
		employee_kpi_values = [{
				'employee_kpi_batch_id' : self.id,
				'employee_id' : employee.id,
				'employee_monthly_kpi_line' : monthly_kpi_line_values
			} for employee in employee_ids]
		employee_kpi_ids = self.env['employee.kpi'].create(employee_kpi_values)
		return employee_kpi_ids
	
	def _find_monthly_grading(self, monthly_ids, tgl_dibuat):
		monthly_grading_ids = self.env['monthly.grading'].search([('month_id', 'in', monthly_ids.ids), ('tahun', '=', tgl_dibuat.strftime('%Y'))])
		# cek apakah ada grading bulanan yang belum terbentuk, jika ada maka buat grading bulanan dan masukkan ke dalam monthly_grading_ids
		# sintaks symmetric_difference adalah built-in function tipe data set, yg berfungsi utk mencari perbedaan dari 2 dataset
		monthly_grading_to_create = list(set(monthly_ids.ids).symmetric_difference(set(monthly_grading_ids.month_id.ids)))
		if monthly_grading_to_create:
			grading_template_values = [(Command.create({
				'grade_template_id' : template.id,
				'grade' : template.grade,
				'nilai_min' : template.nilai_min,
				'nilai_max' : template.nilai_max,
			})) for template in self.env['grading.template'].search([])]
			values = [{
				'periode_id' : self.periode_id.id,
				'month_id' : monthly_grading,
				'tahun' : self.tgl_dibuat.strftime("%Y"),
				'resume_kpi_grading_ids' : grading_template_values,
			} for monthly_grading in monthly_grading_to_create]
			created_monthly_grading_ids = self.env['monthly.grading'].create(values)
			# pertanyaan, apakah tanda |= pada odoo dapat diartikan menambahkan recordset yg baru ke recordset yg sudah ada ?
			monthly_grading_ids |= created_monthly_grading_ids


		return monthly_grading_ids
	
	def button_confirm(self):
		employee_kpi_ids = self._create_employee_kpi()
		# 1. periksa apakah rekap grading bulanan sudah ada? gunakan method find_monthly_grading(month_id, year)
		monthly_grading_ids = self._find_monthly_grading(self.month_ids, self.tgl_dibuat)
		employee_kpi_grading_ids = monthly_grading_ids._create_employee_kpi_grading(employee_kpi_ids.employee_monthly_kpi_line)
		return self.write({'state' : 'in_progress'})
	
	# def _create_
	
	def button_submit(self):
		return self.write({'state' : 'approval_1'})
	
	def _compute_show_approval_button(self):
		self.show_approval_button = False
		if (self.state == 'approval_1' and self.env.user == self.user_approval_1) or \
			  (self.state == 'approval_2' and self.env.user == self.user_approval_2):
			self.show_approval_button = True

	def button_approve_1(self):
		return self.write({'state' : 'approval_2'})
	
	def button_done(self):
		return self.write({'state' : 'done'})
	
	def button_cancel(self):
		return self.write({'state' : 'cancel'})
	
class EmployeeKpi(models.Model):
	_name = 'employee.kpi'
	_description = 'Employee KPI'
	_rec_name = 'employee_id'

	# name = fields.Char(string='Name')
	employee_kpi_batch_id = fields.Many2one(comodel_name='employee.kpi.batch', string='Employee KPI Batch')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan')
	total_resign = fields.Integer(string='Total Resign', compute='_compute_total')
	total_rekrutmen = fields.Integer(string='Total Rekrutmen', compute='_compute_total')
	total_tl = fields.Integer(string='Total TL', compute='_compute_total')
	company_id = fields.Many2one(comodel_name='res.company', string='Company', related='employee_kpi_batch_id.company_id', store=True, precompute=True)
	employee_monthly_kpi_line = fields.One2many(comodel_name='employee.monthly.kpi.line', inverse_name='employee_kpi_id', string='Insentif RO Employee Line')
	average = fields.Float(string='Average', compute='_compute_average')
	grade_average_id = fields.Many2one('resume.kpi.grading',string='Grade Average', compute='_compute_average')
	wilayah_suffer_id = fields.Many2one(comodel_name='wilayah.suffer', string='Wilayah Suffer')
	state = fields.Selection(string='State', related='employee_kpi_batch_id.state')

	@api.depends('employee_monthly_kpi_line.employee_kpi_grading_ids')
	def _compute_average(self):
		for rec in self:
			average_pencapaian, grade_average_id = rec.employee_monthly_kpi_line.employee_kpi_grading_ids._calc_average()
			rec.average = average_pencapaian
			rec.grade_average_id = grade_average_id.id

	def action_show_details(self):
		self.ensure_one()
		view = self.env.ref('mum_kpi.employee_kpi_view_form')
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
	
	@api.depends(
		'employee_monthly_kpi_line.resign', 
		'employee_monthly_kpi_line.rekrutmen', 
		'employee_monthly_kpi_line.tl'
	)
	def _compute_total(self):
		for rec in self:
			rec.total_resign = sum(rec.employee_monthly_kpi_line.mapped('resign'))
			rec.total_rekrutmen = sum(rec.employee_monthly_kpi_line.mapped('rekrutmen'))
			rec.total_tl = sum(rec.employee_monthly_kpi_line.mapped('tl'))

class InsentifRoEmployeeLine(models.Model):
	_name = 'employee.monthly.kpi.line'
	_description = 'Employee Monthly KPI Line'


	employee_kpi_batch_id = fields.Many2one(comodel_name='employee.kpi.batch', string='Employee KPI Batch')
	employee_kpi_id = fields.Many2one(comodel_name='employee.kpi', string='Employee KPI')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan', related='employee_kpi_id.employee_id')
	name = fields.Char(string='Name')
	month_id = fields.Many2one(comodel_name='res.month', string='Bulan')
	cabang = fields.Integer(string='Cabang', default=0)
	formasi = fields.Integer(string='Formasi', default=0)
	aktif = fields.Integer(string='Aktif', default=0)
	resign = fields.Integer(string='Resign', default=0)
	rekrutmen = fields.Integer(string='Rekrutmen', default=0)
	tl = fields.Integer(string='TL', default=0)
	kurang = fields.Integer(string='Kurang', compute='_compute_kurang_pemenuhan')
	pemenuhan = fields.Float(string='Pemenuhan', compute='_compute_kurang_pemenuhan')
	employee_kpi_grading_ids = fields.One2many(comodel_name='employee.kpi.grading', inverse_name='employee_monthly_kpi_line_id', string='Employee KPI Grading')
	# wilayah_suffer_id = fields.Many2one(comodel_name='wilayah.suffer', string='Wilayah Suffer')
	company_id = fields.Many2one(comodel_name='res.company', string='Company', related='employee_kpi_batch_id.company_id', store=True, precompute=True)

	@api.depends('formasi', 'aktif', 'resign', 'rekrutmen')
	def _compute_kurang_pemenuhan(self):
		for rec in self:
			rec.kurang = rec.pemenuhan = 0
			if rec.formasi > 0:
				rec.kurang = rec.formasi - rec.aktif
				rec.pemenuhan = rec.aktif / rec.formasi


	def _create_employee_kpi_grading(self, monthly_grading_ids):
		# for monthly_grading in monthly_grading_ids:

		for line in self:
			employee_kpi_grading_vals = [{
				'monthly_grading_id' : monthly_grading.id,
				'employee_id' : line.employee_id.id,
				'employee_monthly_kpi_line_id' : line.id,
				'employee_kpi_id' : line.employee_kpi_batch_id.id,
			} for monthly_grading in monthly_grading_ids]
			employee_kpi_grading_ids = self.env['employee.kpi.grading'].create(employee_kpi_grading_vals)




