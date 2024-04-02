from odoo import _, api, fields, models, Command
from collections import OrderedDict

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
	avg_maintain_pertama = fields.Float(string='Avg Maintain Pertama')
	grade_average_id = fields.Many2one('grading.template',string='Grade Average', compute='_compute_average')
	wilayah_suffer_id = fields.Many2one(comodel_name='wilayah.suffer', string='Wilayah Suffer')
	
	absen = fields.Integer(string='Absen', compute='_compute_absen_more')
	more = fields.Integer(string='MORE', compute='_compute_absen_more', help='Jumlah Kandidat yang ada di MORE')
	state = fields.Selection(string='State', related='employee_kpi_batch_id.state')
	insentif_wilayah_suffer = fields.Float(string='Insentif Wilayah Suffer', related='wilayah_suffer_id.nilai_insentif', store=True)
	insentif_maintain = fields.Float(string='Insentif Aktif', compute='_compute_insentif')
	insentif_rekrutmen = fields.Float(string='Insentif Rekrutmen', compute='_compute_insentif')
	insentif_tl = fields.Float(string='Insentif TL', compute='_compute_insentif')
	total_insentif = fields.Float(string='Total Insentif', compute='_compute_insentif')
	usulan_kabag = fields.Float(string='Usulan Kabag')
	penyesuaian_kabag = fields.Float(string='Penyesuaian Kabag', compute='_compute_penyesuaian_kabag')
	alasan_penyesuaian = fields.Char(string='Alasan Penyesuaian')
	komite = fields.Float(string='Komite')

	employee_monthly_kpi_line = fields.One2many(comodel_name='employee.monthly.kpi.line', inverse_name='employee_kpi_id', string='Insentif RO Employee Line')

	def _compute_pencapaian_maintain(self):
		avg_maintain_pertama = self.avg_maintain_pertama
		data = OrderedDict(zip(self.employee_monthly_kpi_line.mapped('sequence'),
						  self.employee_monthly_kpi_line.mapped('pemenuhan')))
		pencapaian_maintain_dict = OrderedDict()
		for key, values in data.items():
			if key == 1:
				pencapaian_maintain_dict[key] = (avg_maintain_pertama + data[key]) / 2
			else:
				pencapaian_maintain_dict[key] = (data[key] + data[key - 1]) / 2

		for line in self.employee_monthly_kpi_line:
			line.pencapaian_maintain = pencapaian_maintain_dict[line.sequence]

	@api.depends('usulan_kabag', 'total_insentif')
	def _compute_penyesuaian_kabag(self):
		for rec in self:
			rec.penyesuaian_kabag = rec.usulan_kabag > 0 and rec.usulan_kabag - rec.total_insentif

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

	@api.depends('employee_monthly_kpi_line')
	def _compute_average(self):
		for rec in self:
			average_pencapaian, grade_average_id = rec.employee_monthly_kpi_line._calc_average()
			rec.average = average_pencapaian
			rec.grade_average_id = grade_average_id

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
	_order = 'sequence'

	sequence = fields.Integer(string='Sequence', default=0)
	employee_kpi_batch_id = fields.Many2one(comodel_name='employee.kpi.batch', string='Employee KPI Batch')
	employee_kpi_id = fields.Many2one(comodel_name='employee.kpi', string='Employee KPI', ondelete='cascade')
	monthly_grading_id = fields.Many2one(comodel_name='monthly.grading', string='Monthly Grading')
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
	insentif_maintain = fields.Float(string='Insentif Aktif', related='grade_maintain_id.insentif_maintain', store=True, precompute=True)
	insentif_rekrutmen = fields.Float(string='Insentif Rekrutmen', related='grade_rekrutmen_id.insentif_rekrutmen', store=True, precompute=True)
	insentif_tl = fields.Float(string='Insentif TL', related='grade_tl_id.insentif_tl', store=True, precompute=True)
	kurang = fields.Integer(string='Kurang', compute='_compute_kurang_pemenuhan')
	pemenuhan = fields.Float(string='Pemenuhan', compute='_compute_kurang_pemenuhan')
	company_id = fields.Many2one(comodel_name='res.company', string='Company', related='employee_kpi_batch_id.company_id', store=True, precompute=True)

	pencapaian_rekrutmen = fields.Float(string='Pencapaian Rekrutment', compute='_compute_pencapaian_karyawan', store=True, precompute=True)
	pencapaian_maintain = fields.Float(string='Pencapaian Maintain', compute='_compute_pencapaian_karyawan', store=True, precompute=True)
	pencapaian_tl = fields.Float(string='Pencapaian TL', compute='_compute_pencapaian_karyawan', store=True, precompute=True)
	pencapaian_average = fields.Float(string='Average', compute='_compute_pencapaian_karyawan', store=True, precompute=True)
	grade_rekrutmen_id = fields.Many2one('grading.template',string='Grade Rekrutmen', compute='_compute_pencapaian_karyawan', store=True, precompute=True)
	grade_maintain_id = fields.Many2one('grading.template',string='Grade maintain', compute='_compute_pencapaian_karyawan', store=True, precompute=True)
	grade_tl_id = fields.Many2one('grading.template',string='Grade TL', compute='_compute_pencapaian_karyawan', store=True, precompute=True)
	grade_average_id = fields.Many2one('resume.kpi.grading',string='Grade Average', compute='_compute_pencapaian_karyawan', store=True, precompute=True)

	def _calc_average(self):
		pencapaian_vals = []
		for rec in self:
			pencapaian_vals.extend([rec.pencapaian_rekrutmen, rec.pencapaian_maintain, rec.pencapaian_tl])

		len_pencapaian = len(pencapaian_vals)
		average_pencapaian = sum(pencapaian_vals) / len_pencapaian
		domain = self._get_domain_grading(average_pencapaian)
		average_grade_id = self.env['grading.template'].search(domain, limit=1, order='nilai_max_ro desc')
		return average_pencapaian, average_grade_id
			


	@api.depends(
		'formasi',
		'employee_kpi_id',
		'employee_kpi_id.avg_maintain_pertama',
		'aktif',
		'resign',
		'rekrutmen',
		'tl',
		'kurang',
		'pemenuhan'
		)
	def _compute_pencapaian_karyawan(self):
		kpi_grading_ids = self.monthly_grading_id.resume_kpi_grading_ids
		
		for rec in self:
			# Rekrutmen = rekrutmen / formasi
			# maintain = average(pemenuhan / pemenuhan periode)
			# tl = tl / formasi kurangx
			rec.pencapaian_rekrutmen = rec.pencapaian_tl = 0
			if rec.kurang > 0:
				pencapaian_rekrutmen = rec.rekrutmen / rec.kurang
				rec.pencapaian_rekrutmen = pencapaian_rekrutmen <= 0 and 0 or pencapaian_rekrutmen
				pencapaian_tl = rec.tl / rec.kurang
				rec.pencapaian_tl = pencapaian_tl <= 0 and 0 or pencapaian_tl

			# rec.pencapaian_maintain = pencapaian_maintain_dict[rec.sequence]
			rec.employee_kpi_id._compute_pencapaian_maintain()
				
			# Hitung Grading
			domain_search_grade_rekrutmen = self._get_domain_grading(rec.pencapaian_rekrutmen)
			rec.grade_rekrutmen_id = self.env['grading.template'].search(domain_search_grade_rekrutmen, limit=1, order='nilai_max_ro desc')
			domain_search_grade_tl = self._get_domain_grading(rec.pencapaian_tl)
			rec.grade_tl_id = self.env['grading.template'].search(domain_search_grade_tl, limit=1, order='nilai_max_ro desc')
			domain_search_grade_maintain = self._get_domain_grading(rec.pencapaian_maintain)
			rec.grade_maintain_id = self.env['grading.template'].search(domain_search_grade_maintain, limit=1, order='nilai_max_ro desc')

	def _get_domain_grading(self, field):
		return [('nilai_min_ro', '<=', field), ('nilai_max_ro', '>', field)]

	@api.depends(
		'grade_maintain_id',
		'grade_tl_id',
		'grade_rekrutmen_id',
	)
	def _compute_insentif(self):
		for rec in self:
			rec.insentif_maintain = sum(rec.grade_maintain_id.mapped('insentif_maintain'))
			rec.insentif_tl = sum(rec.grade_tl_id.mapped('insentif_tl'))
			rec.insentif_rekrutmen = sum(rec.grade_rekrutmen_id.mapped('insentif_rekrutmen'))

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
		for line in self:
			employee_kpi_grading_vals = [{
				'monthly_grading_id' : monthly_grading.id,
				'employee_id' : line.employee_id.id,
				# 'employee_monthly_kpi_line_id' : line.id,
				'employee_kpi_id' : line.employee_kpi_batch_id.id,
			} for monthly_grading in monthly_grading_ids]
			employee_kpi_grading_ids = self.env['employee.kpi.grading'].create(employee_kpi_grading_vals)