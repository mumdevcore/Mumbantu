from odoo import _, api, fields, models, Command

class EmployeeKpi(models.Model):
	_name = 'employee.kpi'
	_description = 'Employee KPI'
	_rec_name = 'employee_id'

	# name = fields.Char(string='Name')
	employee_kpi_batch_id = fields.Many2one(comodel_name='employee.kpi.batch', string='Employee KPI Batch', ondelete='cascade')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan')
	total_resign = fields.Integer(string='Total Resign', compute='_compute_total')
	total_rekrutmen = fields.Integer(string='Total Rekrutmen', compute='_compute_total')
	total_tl = fields.Integer(string='Total TL', compute='_compute_total')
	company_id = fields.Many2one(comodel_name='res.company', string='Company', related='employee_kpi_batch_id.company_id', store=True, precompute=True)
	average = fields.Float(string='Average', compute='_compute_average')
	grade_average_id = fields.Many2one('grading.template',string='Grade Average', compute='_compute_average')
	wilayah_suffer_id = fields.Many2one(comodel_name='wilayah.suffer', string='Wilayah Suffer')
	
	absen = fields.Integer(string='Absen', compute='_compute_absen_more')
	more = fields.Integer(string='MORE', compute='_compute_absen_more', help='Jumlah Kandidat yang ada di MORE')
	state = fields.Selection(string='State', related='employee_kpi_batch_id.state')
	insentif_wilayah_suffer = fields.Float(string='Insentif Wilayah Suffer', related='wilayah_suffer_id.nilai_insentif', store=True)
	insentif_maintain = fields.Float(string='Insentif Aktif', compute='_compute_insentif', store=True)
	insentif_rekrutmen = fields.Float(string='Insentif Rekrutmen', compute='_compute_insentif', store=True)
	insentif_tl = fields.Float(string='Insentif TL', compute='_compute_insentif', store=True)
	total_insentif = fields.Float(string='Total Insentif', compute='_compute_insentif', store=True)
	employee_monthly_kpi_line = fields.One2many(comodel_name='employee.monthly.kpi.line', inverse_name='employee_kpi_id', string='Insentif RO Employee Line')

	@api.depends(
		'employee_monthly_kpi_line.insentif_maintain', 
		'employee_monthly_kpi_line.insentif_tl', 
		'employee_monthly_kpi_line.insentif_rekrutmen',
		'insentif_wilayah_suffer',
	)
	def _compute_insentif(self):
		for rec in self:
			rec.insentif_maintain = sum(rec.employee_monthly_kpi_line.mapped('insentif_maintain'))
			rec.insentif_tl = sum(rec.employee_monthly_kpi_line.mapped('insentif_tl'))
			rec.insentif_rekrutmen = sum(rec.employee_monthly_kpi_line.mapped('insentif_rekrutmen'))
			rec.total_insentif = rec.insentif_maintain + rec.insentif_tl + rec.insentif_rekrutmen + rec.insentif_wilayah_suffer
			
	def _compute_absen_more(self):
		for rec in self:
			rec.absen = sum(l.absen for l in rec.employee_monthly_kpi_line)
			rec.more = sum(l.more for l in rec.employee_monthly_kpi_line)

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

class EmployeeMonthlyKpiLine(models.Model):
	_name = 'employee.monthly.kpi.line'
	_description = 'Employee Monthly KPI Line'


	employee_kpi_batch_id = fields.Many2one(comodel_name='employee.kpi.batch', string='Employee KPI Batch')
	employee_kpi_id = fields.Many2one(comodel_name='employee.kpi', string='Employee KPI', ondelete='cascade')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan', related='employee_kpi_id.employee_id')
	name = fields.Char(string='Name')
	month_id = fields.Many2one(comodel_name='res.month', string='Bulan')
	absen = fields.Integer(string='Absen')
	more = fields.Integer(string='MORE', help='Jumlah Kandidat yang ada di MORE')
	cabang = fields.Integer(string='Cabang', default=0)
	formasi = fields.Integer(string='Formasi', default=0)
	aktif = fields.Integer(string='Aktif', default=0)
	resign = fields.Integer(string='Resign', default=0)
	rekrutmen = fields.Integer(string='Rekrutmen', default=0)
	tl = fields.Integer(string='TL', default=0)
	insentif_maintain = fields.Float(string='Insentif Aktif', compute='_compute_insentif', store=True)
	insentif_rekrutmen = fields.Float(string='Insentif Rekrutmen', compute='_compute_insentif', store=True)
	insentif_tl = fields.Float(string='Insntif TL', compute='_compute_insentif', store=True)
	kurang = fields.Integer(string='Kurang', compute='_compute_kurang_pemenuhan')
	pemenuhan = fields.Float(string='Pemenuhan', compute='_compute_kurang_pemenuhan')
	employee_kpi_grading_ids = fields.One2many(comodel_name='employee.kpi.grading', inverse_name='employee_monthly_kpi_line_id', string='Employee KPI Grading')
	# wilayah_suffer_id = fields.Many2one(comodel_name='wilayah.suffer', string='Wilayah Suffer')
	company_id = fields.Many2one(comodel_name='res.company', string='Company', related='employee_kpi_batch_id.company_id', store=True, precompute=True)

	@api.depends('employee_kpi_grading_ids')
	def _compute_insentif(self):
		for rec in self:
			rec.insentif_maintain = sum(rec.employee_kpi_grading_ids.grade_maintain_id.mapped('insentif_maintain'))
			rec.insentif_tl = sum(rec.employee_kpi_grading_ids.grade_tl_id.mapped('insentif_tl'))
			rec.insentif_rekrutmen = sum(rec.employee_kpi_grading_ids.grade_rekrutmen_id.mapped('insentif_rekrutmen'))

	@api.depends('formasi', 'aktif', 'resign', 'rekrutmen')
	def _compute_kurang_pemenuhan(self):
		for rec in self:
			rec.kurang = rec.pemenuhan = 0
			if rec.formasi > 0:
				kurang = rec.formasi - rec.aktif 
				rec.kurang = kurang > 0 and kurang
				pemenuhan = rec.aktif / rec.formasi
				rec.pemenuhan = pemenuhan <= 1 and pemenuhan or 1


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