from odoo import _, api, fields, models, Command


class EmployeeAlwKpi(models.Model):
	_name = 'employee.alw.kpi'
	_description = "Employee Admin KPI"
	_rec_name = 'employee_id'

	employee_kpi_batch_id = fields.Many2one(comodel_name='employee.kpi.batch', string='Employee KPI Batch')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan')
	absen = fields.Integer(string='Absen', compute='_compute_absen')
	total_karyawan_terakhir = fields.Integer(string='Karyawan Terakhir', compute='_compute_all')
	total_aktif = fields.Integer(string='Aktif', compute='_compute_all')
	total_resign = fields.Integer(string='Resign', compute='_compute_all')
	total_perp_kontrak = fields.Integer(string='Perp. Kontrak', compute='_compute_all')
	total_incomplete_data = fields.Integer(string='Incomplete Data', compute='_compute_all')
	persen_incomplete_data = fields.Float(string='Incomplete Data', compute='_compute_all')
	total_pkwt = fields.Integer(string='PKWT', compute='_compute_all')
	persen_pkwt = fields.Float(string='PKWT', compute='_compute_all')
	total_ppkwt = fields.Integer(string='PPKWT', compute='_compute_all')
	persen_ppkwt = fields.Float(string='PPKWT', compute='_compute_all')
	total_kesalahan_resign = fields.Integer(string='Kesalahan Resign', compute='_compute_all')
	persen_kesalahan_resign = fields.Float(string='Kesalahan Resign', compute='_compute_all')
	average_alw = fields.Float(string='Average ALW', compute='_compute_all')
	# grade_incomplete_data_id = fields.Many2one('resume.kpi.grading',string='Grade Incomplete Data', compute='_compute_all')
	# grade_pkwt_id = fields.Many2one('resume.kpi.grading',string='Grade PKWT', compute='_compute_all')
	# grade_ppkwt_id = fields.Many2one('resume.kpi.grading',string='Grade PPKWT', compute='_compute_all')
	# grade_kesalahan_resign_id = fields.Many2one('resume.kpi.grading',string='Grade Kesalahan Resign', compute='_compute_all')
	# grade_average_id fields.Many2one(comodel_name='resume.kpi.grading', string='Grade Average', compute='_compute_all)
	grade_incomplete_data_id = fields.Many2one('grading.template',string='Grade Incomplete Data', compute='_compute_all')
	grade_pkwt_id = fields.Many2one('grading.template',string='Grade PKWT', compute='_compute_all')
	grade_ppkwt_id = fields.Many2one('grading.template',string='Grade PPKWT', compute='_compute_all')
	grade_kesalahan_resign_id = fields.Many2one('grading.template',string='Grade Kesalahan Resign', compute='_compute_all')
	grade_average_id = fields.Many2one(comodel_name='grading.template', string='Grade Average')
	
	state = fields.Selection(string='State', related='employee_kpi_batch_id.state')

	alw_monthly_kpi_line = fields.One2many(comodel_name='alw.monthly.kpi.line', inverse_name='employee_alw_kpi_id', string='ALW Monthly KPI')

	def _compute_absen(self):
		for rec in self:
			rec.absen = sum(l.absen for l in rec.alw_monthly_kpi_line)

	@api.depends('alw_monthly_kpi_line')
	def _compute_all(self):
		for rec in self:
			total_line = len(rec.alw_monthly_kpi_line)
			rec.total_karyawan_terakhir = rec.alw_monthly_kpi_line and rec.alw_monthly_kpi_line[-1].karyawan_terakhir or 0
			rec.total_aktif = sum(line.aktif for line in rec.alw_monthly_kpi_line)
			rec.total_resign = sum(line.resign for line in rec.alw_monthly_kpi_line)
			rec.total_perp_kontrak = sum(line.perp_kontrak for line in rec.alw_monthly_kpi_line)
			rec.total_incomplete_data = sum(line.incomplete_data for line in rec.alw_monthly_kpi_line)
			rec.total_pkwt = sum(line.pkwt for line in rec.alw_monthly_kpi_line)
			rec.total_ppkwt = sum(line.ppkwt for line in rec.alw_monthly_kpi_line)
			rec.total_kesalahan_resign = sum(line.kesalahan_resign for line in rec.alw_monthly_kpi_line)

			rec.persen_incomplete_data = rec.total_aktif > 0 and rec.total_incomplete_data / rec.total_aktif or 0
			rec.persen_pkwt = rec.total_aktif > 0 and rec.total_pkwt / rec.total_aktif or 0
			rec.persen_ppkwt = rec.total_perp_kontrak > 0 and rec.total_ppkwt / rec.total_perp_kontrak or 0
			rec.persen_kesalahan_resign = rec.total_resign > 0 and rec.total_kesalahan_resign / rec.total_resign or 0

			percent_field_values = [rec.persen_incomplete_data, rec.persen_pkwt, rec.persen_ppkwt, rec.persen_kesalahan_resign]
			rec.average_alw = sum(percent_field_values) / len(percent_field_values)

			domain_search_incomplete_data = self._get_domain_grading('incomplete_data', rec.persen_incomplete_data)
			rec.grade_incomplete_data_id = self.env['grading.template'].search(domain_search_incomplete_data, limit=1, order='nilai_max_alw_incomplete_data desc')
			
			
			domain_search_pkwt = self._get_domain_grading('pkwt', rec.persen_pkwt)
			rec.grade_pkwt_id = self.env['grading.template'].search(domain_search_pkwt, limit=1, order='nilai_max_alw_pkwt desc')
			
			domain_search_ppkwt = self._get_domain_grading('ppkwt', rec.persen_ppkwt)
			rec.grade_ppkwt_id = self.env['grading.template'].search(domain_search_ppkwt, limit=1, order='nilai_max_alw_ppkwt desc')

			domain_search_resign = self._get_domain_grading('resign', rec.persen_kesalahan_resign)
			rec.grade_kesalahan_resign_id = self.env['grading.template'].search(domain_search_resign, limit=1, order='nilai_max_alw_resign desc')
			
			domain_search_avg = self._get_domain_grading('avg', rec.average_alw)
			rec.grade_average_id = self.env['grading.template'].search(domain_search_avg, limit=1, order='nilai_max_alw_resign desc')

	def _get_domain_grading(self, key, field):
		nilai_min = f'nilai_min_alw_{key}'
		nilai_max = f'nilai_max_alw_{key}'
		return [(nilai_min, '<=', field), (nilai_max, '>', field)]

	def action_show_details(self):
		self.ensure_one()
		view = self.env.ref('mum_kpi.employee_alw_kpi_view_form')
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

class AlwMonthlyKpiLine(models.Model):
	_name = 'alw.monthly.kpi.line'
	_description = 'ALW Monthly KPI Line'

	# name = fields.Char()
	employee_kpi_batch_id = fields.Many2one(comodel_name='employee.kpi.batch', string='Employee KPI Batch')
	monthly_grading_id = fields.Many2one(comodel_name='monthly.grading', string='Monthly Grading')
	employee_alw_kpi_id = fields.Many2one(comodel_name='employee.alw.kpi', string='Employee KPI')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan', related='employee_alw_kpi_id.employee_id')
	absen = fields.Integer(string='Absen')
	name = fields.Char(string='Name')
	month_id = fields.Many2one(comodel_name='res.month', string='Bulan')
	karyawan_terakhir = fields.Integer(string='Karyawan Terakhir')
	aktif = fields.Integer(string='Aktif')
	resign = fields.Integer(string='Resign')
	perp_kontrak = fields.Integer(string='Perp. Kontrak')
	incomplete_data = fields.Integer(string='Incomplete Data')
	pkwt = fields.Integer(string='PKWT')
	ppkwt = fields.Integer(string='PPKWT')
	kesalahan_resign = fields.Integer(string='Kesalahan Resign')

	
