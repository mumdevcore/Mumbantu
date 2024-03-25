from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError


class GradingMasterTemplate(models.Model):
	_name = 'grading.template'
	_description = 'Grading Master Template'
	_rec_name = 'grade'

	# Nilai ditulis dalam persen, pastikan memberikan widget percentage pada xml
	grade = fields.Char(string='Grade')
	nilai_min = fields.Float(string='Nilai Min', default=0)
	nilai_max = fields.Float(string='Nilai Max', default=0)
	nilai_min_ro = fields.Float(string='Min RO', default=0)
	nilai_max_ro = fields.Float(string='Max RO', default=0)
	insentif_rekrutmen = fields.Float(string='Insentif Rekrutmen', default=0)
	insentif_maintain = fields.Float(string='Insentif Maintain', default=0)
	insentif_tl = fields.Float(string='Insentif TL', default=0)


	nilai_min_alw_resign = fields.Float(string='Min ALW Resign', default=0)
	nilai_max_alw_resign = fields.Float(string='Max ALW Resign', default=0)
	nilai_min_alw_incomplete_data = fields.Float(string='Min ALW Incomplete Data', default=0)
	nilai_max_alw_incomplete_data = fields.Float(string='Max ALW Incomplete Data', default=0)
	nilai_min_alw_pkwt = fields.Float(string='Min ALW PKWT', default=0)
	nilai_max_alw_pkwt = fields.Float(string='Max ALW PKWT', default=0)
	nilai_min_alw_ppkwt = fields.Float(string='Min ALW PPKWT', default=0)
	nilai_max_alw_ppkwt = fields.Float(string='Max ALW PPKWT', default=0)
	nilai_min_alw_avg = fields.Float(string='Min ALW Average', default=0)
	nilai_max_alw_avg = fields.Float(string='Max ALW Average', default=0)
	insentif_alw_resign = fields.Float(string='Insentif ALW Resign', default=0)
	insentif_alw_incomplete_data = fields.Float(string='Insentif ALW Incomplete Data', default=0)
	insentif_alw_pkwt = fields.Float(string='Insentif ALW PKWT', default=0)
	insentif_alw_ppkwt = fields.Float(string='Insentif ALW PPKWT', default=0)

	nilai_min_kro = fields.Float(string='Min KRO', default=0)
	nilai_max_kro = fields.Float(string='Max KRO', default=0)
	insentif_kro = fields.Float(string='Insentif KRO', default=0)

	wilayah_suffer_id  = fields.Many2one(comodel_name='wilayah.suffer', string='Wilayah Suffer')


class GradingMaster(models.Model):
	_name = 'monthly.grading'
	_description = 'Grading Bulanan'

	name = fields.Char(string='Name')
	periode_id = fields.Many2one(comodel_name='kpi.periode', string='Periode')
	month_id = fields.Many2one(comodel_name='res.month', string='Month')
	tahun = fields.Char(string='Tahun')
	employee_kpi_grading_ids = fields.One2many(comodel_name='employee.kpi.grading', inverse_name='monthly_grading_id', string='Employee KPI Grading', ondelete='cascade')
	resume_kpi_grading_ids = fields.One2many(comodel_name='resume.kpi.grading', inverse_name='monthly_grading_id', string='Resume KPI Grading', ondelete='cascade')

	@api.model
	def create(self, values):
		month_id = self.env['res.month'].browse(values.get('month_id'))
		if not month_id or not values.get('tahun'):
			raise ValidationError(_("Bulan dan Tahun harus diisi."))
		values['name'] = f"{month_id.name}-{values.get('tahun')}"
		return super(GradingMaster, self).create(values)
	
	def _create_employee_kpi_grading(self, employee_monthly_kpi_line_ids):
		employee_kpi_grading_ids = self.env['employee.kpi.grading']

		for grading in self:
			filtered_employee_kpi_line_ids = employee_monthly_kpi_line_ids.filtered(lambda l:l.month_id == grading.month_id)
			employee_kpi_grading_vals = [{
				'monthly_grading_id' : grading.id,
				'employee_id' : employee_kpi_line_id.employee_id.id,
				'employee_monthly_kpi_line_id' : employee_kpi_line_id.id,
			} for employee_kpi_line_id in filtered_employee_kpi_line_ids]
			employee_kpi_grading_ids.create(employee_kpi_grading_vals)
		
		return employee_kpi_grading_ids

class GradingEmployeeMonth(models.Model):
	_name = 'employee.kpi.grading'
	_description = "Employee KPI Grading"

	monthly_grading_id = fields.Many2one(comodel_name='monthly.grading', string='Monthly Grading')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan')
	employee_monthly_kpi_line_id = fields.Many2one(comodel_name='employee.monthly.kpi.line', string='Employee Monthly KPI', ondelete='cascade')
	absen = fields.Integer(string='Absen', related='employee_monthly_kpi_line_id.absen')
	more = fields.Integer(string='MORE', related='employee_monthly_kpi_line_id.more')
	employee_kpi_id = fields.Many2one(comodel_name='employee.kpi', string='Employee KPI')
	pencapaian_rekrutmen = fields.Float(string='Pencapaian Rekrutment', compute='_compute_pencapaian_karyawan')
	pencapaian_maintain = fields.Float(string='Pencapaian Maintain', compute='_compute_pencapaian_karyawan')
	pencapaian_tl = fields.Float(string='Pencapaian TL', compute='_compute_pencapaian_karyawan')
	# pencapaian_average = fields.Float(string='Average', compute='_compute_pencapaian_karyawan')
	grade_rekrutmen_id = fields.Many2one('grading.template',string='Grade Rekrutmen', compute='_compute_pencapaian_karyawan')
	grade_maintain_id = fields.Many2one('grading.template',string='Grade maintain', compute='_compute_pencapaian_karyawan')
	grade_tl_id = fields.Many2one('grading.template',string='Grade TL', compute='_compute_pencapaian_karyawan')
	# grade_average_id = fields.Many2one('resume.kpi.grading',string='Grade Average', compute='_compute_pencapaian_karyawan')

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
		'employee_kpi_id.employee_monthly_kpi_line',
		'employee_monthly_kpi_line_id.formasi',
		'employee_monthly_kpi_line_id.aktif',
		'employee_monthly_kpi_line_id.resign',
		'employee_monthly_kpi_line_id.rekrutmen',
		'employee_monthly_kpi_line_id.tl',
		'employee_monthly_kpi_line_id.kurang',
		'employee_monthly_kpi_line_id.pemenuhan'
		)
	def _compute_pencapaian_karyawan(self):
		kpi_grading_ids = self.monthly_grading_id.resume_kpi_grading_ids
		for rec in self:
			# Rekrutmen = rekrutmen / formasi
			# maintain = average(pemenuhan / pemenuhan periode)
			# tl = tl / formasi kurang
			rec.pencapaian_rekrutmen = rec.pencapaian_tl = 0
			
			# rec.grade_rekrutmen_id = rec.grade_maintain_id = rec.grade_tl_id = rec.grade_average_id = False
			# if rec.employee_monthly_kpi_line_id.formasi > 0:
				
			if rec.employee_monthly_kpi_line_id.kurang > 0:
				pencapaian_rekrutmen = rec.employee_monthly_kpi_line_id.rekrutmen / rec.employee_monthly_kpi_line_id.kurang
				rec.pencapaian_rekrutmen = pencapaian_rekrutmen <= 1 and pencapaian_rekrutmen or 1
				
				pencapaian_tl = rec.employee_monthly_kpi_line_id.tl / rec.employee_monthly_kpi_line_id.kurang
				rec.pencapaian_tl = pencapaian_tl <= 1 and pencapaian_tl or 1
			rec.pencapaian_maintain = rec.employee_monthly_kpi_line_id.pemenuhan
			

			# Hitung Grading
			domain_search_grade_rekrutmen = self._get_domain_grading(rec.pencapaian_rekrutmen)
			print(domain_search_grade_rekrutmen)
			rec.grade_rekrutmen_id = self.env['grading.template'].search(domain_search_grade_rekrutmen, limit=1, order='nilai_max_ro desc')
			domain_search_grade_tl = self._get_domain_grading(rec.pencapaian_tl)
			rec.grade_tl_id = self.env['grading.template'].search(domain_search_grade_tl, limit=1, order='nilai_max_ro desc')
			domain_search_grade_maintain = self._get_domain_grading(rec.pencapaian_maintain)
			rec.grade_maintain_id = self.env['grading.template'].search(domain_search_grade_maintain, limit=1, order='nilai_max_ro desc')

			# rec.grade_rekrutmen_id = kpi_grading_ids.filtered(lambda s:rec.pencapaian_rekrutmen >= s.nilai_min and rec.pencapaian_rekrutmen < s.nilai_max and rec.pencapaian_rekrutmen > 0).id
			# rec.grade_maintain_id = kpi_grading_ids.filtered(lambda s:rec.pencapaian_maintain >= s.nilai_min and rec.pencapaian_maintain < s.nilai_max and rec.pencapaian_maintain > 0).id
			# rec.grade_tl_id = kpi_grading_ids.filtered(lambda s:rec.pencapaian_tl >= s.nilai_min and rec.pencapaian_tl < s.nilai_max and rec.pencapaian_tl > 0).id

	def _get_domain_grading(self, field):
		return [('nilai_min_ro', '<=', field), ('nilai_max_ro', '>', field)]
			
	
class ResumeKpiGrading(models.Model):
	_name = 'resume.kpi.grading'
	_description = 'Resume KPI Grading'
	_order = 'grade asc'
	_rec_name = 'grade_template_id'

	monthly_grading_id = fields.Many2one(comodel_name='monthly.grading', string='Monthly Grading', ondelete='cascade')
	grade_template_id = fields.Many2one(comodel_name='grading.template', string='Grading Template')
	grade = fields.Char(string='Grade')
	nilai_min_ro = fields.Float(string='Min RO')
	nilai_max_ro = fields.Float(string='Max RO')
	nilai_min_alw_resign = fields.Float(string='Min ALW Resign')
	nilai_max_alw_resign = fields.Float(string='Max ALW Resign')
	nilai_min_alw_incomplete_data = fields.Float(string='Min ALW Incomplete Data')
	nilai_max_alw_incomplete_data = fields.Float(string='Max ALW Incomplete Data')
	nilai_min_alw_pkwt = fields.Float(string='Min ALW PKWT')
	nilai_max_alw_pkwt = fields.Float(string='Max ALW PKWT')
	nilai_min_alw_ppkwt = fields.Float(string='Min ALW PPKWT')
	nilai_max_alw_ppkwt = fields.Float(string='Max ALW PPKWT')
	
	jumlah_ro = fields.Integer(string='Jumlah RO', compute='_compute_jumlah_ro_alw')
	jumlah_alw = fields.Integer(string='Jumlah ALW', compute='_compute_jumlah_ro_alw')
	
	# @api.depends('grade_template_id', 'monthly_grading_id')
	def _compute_jumlah_ro_alw(self):
		for rec in self:
			# kpi_monthly_ids = rec.monthly_grading_id.
			rec.jumlah_ro = 0
			rec.jumlah_alw = 0