from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError


class GradingMasterTemplate(models.Model):
	_name = 'grading.template'
	_description = 'Grading Master Template'
	_rec_name = 'grade'

	grade = fields.Char(string='Grade')
	nilai_min = fields.Float(string='Nilai Min')
	nilai_max = fields.Float(string='Nilai Max')

class GradingMaster(models.Model):
	_name = 'monthly.grading'
	_description = 'Grading Bulanan'

	name = fields.Char(string='Name')
	periode_id = fields.Many2one(comodel_name='kpi.periode', string='Periode')
	month_id = fields.Many2one(comodel_name='res.month', string='Month')
	tahun = fields.Char(string='Tahun')
	employee_kpi_grading_ids = fields.One2many(comodel_name='employee.kpi.grading', inverse_name='monthly_grading_id', string='Employee KPI Grading')
	resume_kpi_grading_ids = fields.One2many(comodel_name='resume.kpi.grading', inverse_name='monthly_grading_id', string='Resume KPI Grading')

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
	employee_monthly_kpi_line_id = fields.Many2one(comodel_name='employee.monthly.kpi.line', string='Employee Monthly KPI')
	employee_kpi_id = fields.Many2one(comodel_name='employee.kpi', string='Employee KPI')
	pencapaian_rekrutmen = fields.Float(string='Pencapaian Rekrutment', compute='_compute_pencapaian_karyawan')
	pencapaian_maintain = fields.Float(string='Pencapaian Maintain', compute='_compute_pencapaian_karyawan')
	pencapaian_tl = fields.Float(string='Pencapaian TL', compute='_compute_pencapaian_karyawan')
	# pencapaian_average = fields.Float(string='Average', compute='_compute_pencapaian_karyawan')
	grade_rekrutmen_id = fields.Many2one('resume.kpi.grading',string='Grade Rekrutmen', compute='_compute_pencapaian_karyawan')
	grade_maintain_id = fields.Many2one('resume.kpi.grading',string='Grade maintain', compute='_compute_pencapaian_karyawan')
	grade_tl_id = fields.Many2one('resume.kpi.grading',string='Grade TL', compute='_compute_pencapaian_karyawan')
	# grade_average_id = fields.Many2one('resume.kpi.grading',string='Grade Average', compute='_compute_pencapaian_karyawan')

	def _calc_average(self):
		pencapaian_vals = []
		for rec in self:
			pencapaian_vals.extend([rec.pencapaian_rekrutmen, rec.pencapaian_maintain, rec.pencapaian_tl])

		len_pencapaian = len(pencapaian_vals)
		average_pencapaian = sum(pencapaian_vals) / len_pencapaian
		domain = self._get_domain_grading(average_pencapaian)
		average_grade_id = self.env['resume.kpi.grading'].search(domain, limit=1, order='nilai_max desc')
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
			rec.pencapaian_maintain = rec.employee_monthly_kpi_line_id.pemenuhan
			# rec.grade_rekrutmen_id = rec.grade_maintain_id = rec.grade_tl_id = rec.grade_average_id = False
			if rec.employee_monthly_kpi_line_id.formasi > 0:
				rec.pencapaian_rekrutmen = (rec.employee_monthly_kpi_line_id.rekrutmen - rec.employee_monthly_kpi_line_id.kurang) / rec.employee_monthly_kpi_line_id.formasi
			if rec.employee_monthly_kpi_line_id.kurang > 0:
				rec.pencapaian_tl = rec.employee_monthly_kpi_line_id.tl / rec.employee_monthly_kpi_line_id.kurang
			
			

			# Hitung Grading
			domain_search_grade_rekrutmen = self._get_domain_grading(rec.pencapaian_rekrutmen)
			rec.grade_rekrutmen_id = self.env['resume.kpi.grading'].search(domain_search_grade_rekrutmen, limit=1, order='nilai_max desc')
			domain_search_grade_tl = self._get_domain_grading(rec.pencapaian_tl)
			rec.grade_tl_id = self.env['resume.kpi.grading'].search(domain_search_grade_tl, limit=1, order='nilai_max desc')
			domain_search_grade_maintain = self._get_domain_grading(rec.pencapaian_maintain)
			rec.grade_maintain_id = self.env['resume.kpi.grading'].search(domain_search_grade_maintain, limit=1, order='nilai_max desc')

			# rec.grade_rekrutmen_id = kpi_grading_ids.filtered(lambda s:rec.pencapaian_rekrutmen >= s.nilai_min and rec.pencapaian_rekrutmen < s.nilai_max and rec.pencapaian_rekrutmen > 0).id
			# rec.grade_maintain_id = kpi_grading_ids.filtered(lambda s:rec.pencapaian_maintain >= s.nilai_min and rec.pencapaian_maintain < s.nilai_max and rec.pencapaian_maintain > 0).id
			# rec.grade_tl_id = kpi_grading_ids.filtered(lambda s:rec.pencapaian_tl >= s.nilai_min and rec.pencapaian_tl < s.nilai_max and rec.pencapaian_tl > 0).id

	def _get_domain_grading(self, field):
		return [('nilai_min', '<=', field), ('nilai_max', '>', field), ('id', 'in', self.monthly_grading_id.resume_kpi_grading_ids.ids)]
			
	
class ResumeKpiGrading(models.Model):
	_name = 'resume.kpi.grading'
	_description = 'Resume KPI Grading'
	_order = 'grade asc'
	_rec_name = 'grade_template_id'

	monthly_grading_id = fields.Many2one(comodel_name='monthly.grading', string='Monthly Grading')
	grade_template_id = fields.Many2one(comodel_name='grading.template', string='Grading Template')
	grade = fields.Char(string='Grade')
	nilai_min = fields.Float(string='Nilai Min')
	nilai_max = fields.Float(string='Nilai Max')
	jumlah_ro = fields.Integer(string='Jumlah RO', compute='_compute_jumlah_ro')
	
	# @api.depends('grade_template_id', 'monthly_grading_id')
	def _compute_jumlah_ro(self):
		for rec in self:
			# kpi_monthly_ids = rec.monthly_grading_id.
			rec.jumlah_ro = 0