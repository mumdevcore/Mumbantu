from odoo import _, api, fields, models, Command


class EmployeeAlwKpi(models.Model):
	_name = 'employee.alw.kpi'
	_description = "Employee Admin KPI"
	_rec_name = 'employee_id'

	employee_kro_kpi_id = fields.Many2one(comodel_name='employee.kro.kpi', string='Employee KPI Batch')
	kpi_mekaar_batch_id = fields.Many2one(comodel_name='kpi.mekaar.batch', string='KPI Mekaar Batch')
	employee_kpi_line_sebelumnya_id = fields.Many2one(comodel_name='employee.alw.kpi', string='KPI ALW Sebelumnya')
	monthly_grading_id = fields.Many2one(comodel_name='monthly.grading', string='Monthly Grading')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan')
	employee_manager_id = fields.Many2one(comodel_name='hr.employee', string='KRO', related='employee_id.parent_id')

	absen = fields.Integer(string='Keterlambatan (Menit)', compute='_compute_absen', store=True, precompute=True)
	tidak_masuk = fields.Integer(string='Tidak Masuk (Hari)', compute='_compute_absen', store=True, precompute=True)
	total_karyawan_terakhir = fields.Integer(string='Karyawan Terakhir', compute='_compute_all', store=True, precompute=True)
	total_aktif = fields.Integer(string='Aktif', compute='_compute_all', store=True, precompute=True)
	total_resign = fields.Integer(string='Resign', compute='_compute_all', store=True, precompute=True)
	total_perp_kontrak = fields.Integer(string='Perp. Kontrak', compute='_compute_all', store=True, precompute=True)
	total_incomplete_data = fields.Integer(string='Incomplete Data', compute='_compute_all', store=True, precompute=True)
	total_pkwt = fields.Integer(string='Belum PKWT', compute='_compute_all', store=True, precompute=True)
	total_ppkwt = fields.Integer(string='Belum PPKWT', compute='_compute_all', store=True, precompute=True)
	total_kesalahan_resign = fields.Integer(string='Kesalahan Resign', compute='_compute_all', store=True, precompute=True)
	
	persen_kesalahan_resign = fields.Float(string='Kesalahan Resign')
	persen_incomplete_data = fields.Float(string='Incomplete Data')
	persen_pkwt = fields.Float(string='Belum PKWT')
	persen_ppkwt = fields.Float(string='Belum PPKWT')
	average_alw = fields.Float(string='Average ALW')
	grade_incomplete_data_id = fields.Many2one('grading.template',string='Grade Incomplete Data')
	grade_pkwt_id = fields.Many2one('grading.template',string='Grade PKWT')
	grade_ppkwt_id = fields.Many2one('grading.template',string='Grade PPKWT')
	grade_kesalahan_resign_id = fields.Many2one('grading.template',string='Grade Kesalahan Resign')
	grade_absen_id = fields.Many2one(comodel_name='grading.template', string='Grade Average')
	grade_average_id = fields.Many2one(comodel_name='grading.template', string='Grade Average')

	insentif_alw_resign = fields.Float(string='Insentif Resign', compute='_compute_insentif', store=True, precompute=True)
	insentif_alw_incomplete_data = fields.Float(string='Insentif Incomplete Data', compute='_compute_insentif', store=True, precompute=True)
	insentif_alw_pkwt = fields.Float(string='Insentif PKWT', compute='_compute_insentif', store=True, precompute=True)
	insentif_alw_ppkwt = fields.Float(string='Insentif PPKWT', compute='_compute_insentif', store=True, precompute=True)
	total_insentif = fields.Float(string='Insentif Total', compute='_compute_insentif', store=True, precompute=True)
	insentif_sebelumnya = fields.Float(string='Insentif Sebelumnya', related='employee_kpi_line_sebelumnya_id.penyesuaian', store=True)
	potongan_absen = fields.Float(string='Potongan Absen', compute='_compute_insentif', store=True, precompute=True)

	usulan_kabag = fields.Float(string='Usulan Kabag')
	penyesuaian_kabag = fields.Float(string='Penyesuaian Kabag', compute='_compute_penyesuaian_kabag')
	alasan_penyesuaian = fields.Char(string='Alasan Penyesuaian')
	penyesuaian = fields.Float(string='Komite')
	# penyesuaian kabag usulan kabag	Periode Sebelumnya Komite
	
	state = fields.Selection(string='State', related='employee_kro_kpi_id.state')

	alw_monthly_kpi_line = fields.One2many(comodel_name='alw.monthly.kpi.line', inverse_name='employee_alw_kpi_id', string='ALW Monthly KPI')

	def action_confirm(self):
		for rec in self:
			rec._compute_all()
			rec._compute_grade()
			rec._compute_insentif()

	@api.depends('usulan_kabag', 'total_insentif')
	def _compute_penyesuaian_kabag(self):
		for rec in self:
			rec.penyesuaian_kabag = rec.usulan_kabag > 0 and rec.usulan_kabag + rec.total_insentif 

	@api.depends('alw_monthly_kpi_line.absen')
	def _compute_absen(self):
		for rec in self:
			rec.absen = sum(l.absen for l in rec.alw_monthly_kpi_line)
			rec.tidak_masuk = sum(l.tidak_masuk for l in rec.alw_monthly_kpi_line)

	@api.depends(
		'alw_monthly_kpi_line.potongan_absen',
		'grade_incomplete_data_id',
		'grade_pkwt_id',
		'grade_ppkwt_id',
		'grade_kesalahan_resign_id',
	)
	def _compute_insentif(self):
		for rec in self:
			rec.insentif_alw_incomplete_data = rec.grade_incomplete_data_id.insentif_alw_incomplete_data
			rec.insentif_alw_pkwt = rec.grade_pkwt_id.insentif_alw_pkwt
			rec.insentif_alw_ppkwt = rec.grade_ppkwt_id.insentif_alw_ppkwt
			rec.insentif_alw_resign = rec.grade_kesalahan_resign_id.insentif_alw_resign
			rec.potongan_absen = sum(line.potongan_absen for line in rec.alw_monthly_kpi_line)
			rec.total_insentif = sum([rec.insentif_alw_incomplete_data, rec.insentif_alw_pkwt, rec.insentif_alw_ppkwt, rec.insentif_alw_resign]) + rec.potongan_absen


	@api.depends(
		'alw_monthly_kpi_line.karyawan_terakhir',
		'alw_monthly_kpi_line.aktif',
		'alw_monthly_kpi_line.resign',
		'alw_monthly_kpi_line.perp_kontrak',
		'alw_monthly_kpi_line.incomplete_data',
		'alw_monthly_kpi_line.pkwt',
		'alw_monthly_kpi_line.ppkwt',
		'alw_monthly_kpi_line.kesalahan_resign',
		'alw_monthly_kpi_line.persen_incomplete_data',
		'alw_monthly_kpi_line.persen_pkwt',
		'alw_monthly_kpi_line.persen_ppkwt',
		'alw_monthly_kpi_line.persen_kesalahan_resign',
	)
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


	@api.onchange(
		'absen',
		'tidak_masuk',
		'total_karyawan_terakhir',
		'total_aktif',
		'total_resign',
		'total_perp_kontrak',
		'total_incomplete_data',
		'total_pkwt',
		'total_ppkwt',
		'total_kesalahan_resign'
	)
	def _compute_grade(self):
		for rec in self:
			total_line = len(rec.alw_monthly_kpi_line)
			rec.persen_incomplete_data = sum(l.incomplete_data for l in rec.alw_monthly_kpi_line) / sum(l.karyawan_terakhir for l in rec.alw_monthly_kpi_line)
			rec.persen_pkwt = sum(l.pkwt for l in rec.alw_monthly_kpi_line) / sum(l.karyawan_terakhir for l in rec.alw_monthly_kpi_line)
			rec.persen_ppkwt = sum(l.ppkwt for l in rec.alw_monthly_kpi_line) / sum(l.perp_kontrak for l in rec.alw_monthly_kpi_line)
			rec.persen_kesalahan_resign = sum(l.kesalahan_resign for l in rec.alw_monthly_kpi_line) / sum(l.resign for l in rec.alw_monthly_kpi_line)

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
	_order = 'sequence'

	# name = fields.Char()
	employee_kro_kpi_id = fields.Many2one(comodel_name='employee.kro.kpi', string='Employee KPI Batch')
	monthly_grading_id = fields.Many2one(comodel_name='monthly.grading', string='Monthly Grading')
	employee_alw_kpi_id = fields.Many2one(comodel_name='employee.alw.kpi', string='Employee KPI')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan', related='employee_alw_kpi_id.employee_id')
	
	sequence = fields.Integer(string='Sequence', default=0)
	name = fields.Char(string='Name')
	month_id = fields.Many2one(comodel_name='res.month', string='Bulan')
	aktif = fields.Integer(string='Aktif')
	absen = fields.Integer(string='Keterlambatan (Menit)')
	tidak_masuk = fields.Integer(string='Tidak Masuk (Hari)',)
	karyawan_terakhir = fields.Integer(string='Jumlah Kelolaan')
	resign = fields.Integer(string='Resign')
	perp_kontrak = fields.Integer(string='Perp. Kontrak')
	incomplete_data = fields.Integer(string='Incomplete Data')
	pkwt = fields.Integer(string='Belum PKWT')
	ppkwt = fields.Integer(string='Belum PPKWT')
	kesalahan_resign = fields.Integer(string='Kesalahan Resign')

	persen_incomplete_data = fields.Float(string='Incomplete Data %')
	persen_pkwt = fields.Float(string='Belum PKWT %')
	persen_ppkwt = fields.Float(string='Belum PPKWT %')
	persen_kesalahan_resign = fields.Float(string='Kesalahan Resign %')

	grade_absen_id = fields.Many2one('grading.template',string='Grade Absensi')
	grade_incomplete_data_id = fields.Many2one('grading.template',string='Grade Incomplete Data')
	grade_pkwt_id = fields.Many2one('grading.template',string='Grade PKWT')
	grade_ppkwt_id = fields.Many2one('grading.template',string='Grade PPKWT')
	grade_kesalahan_resign_id = fields.Many2one('grading.template',string='Grade Kesalahan Resign')

	potongan_absen = fields.Float(string='Potongan Absensi')
	# grade_average_id = fields.Many2one(comodel_name='grading.template', string='Grade Average')

	@api.onchange(
		'absen',
		'karyawan_terakhir',
		'resign',
		'perp_kontrak',
		'incomplete_data',
		'pkwt',
		'ppkwt',
		'kesalahan_resign',
	)
	def _compute_all(self):
		for rec in self:
			rec.persen_incomplete_data = rec.karyawan_terakhir > 0 and rec.incomplete_data / rec.karyawan_terakhir or 1
			rec.persen_pkwt = rec.karyawan_terakhir > 0 and rec.pkwt / rec.karyawan_terakhir or 1
			rec.persen_ppkwt = rec.perp_kontrak > 0 and rec.ppkwt / rec.perp_kontrak or 1
			rec.persen_kesalahan_resign = rec.resign > 0 and rec.kesalahan_resign / rec.resign or 1

			# percent_field_values = [rec.persen_incomplete_data, rec.persen_pkwt, rec.persen_ppkwt, rec.persen_kesalahan_resign]
			# rec.average_alw = sum(percent_field_values) / len(percent_field_values)
			domain_search_absen = self._get_domain_grading('absen', rec.absen)
			
			rec.grade_absen_id = self.env['grading.template'].search(domain_search_absen, limit=1, order='nilai_max_absen desc')

			domain_search_incomplete_data = self._get_domain_grading('alw_incomplete_data', rec.persen_incomplete_data)
			rec.grade_incomplete_data_id = self.env['grading.template'].search(domain_search_incomplete_data, limit=1, order='nilai_max_alw_incomplete_data desc')
			
			
			domain_search_pkwt = self._get_domain_grading('alw_pkwt', rec.persen_pkwt)
			rec.grade_pkwt_id = self.env['grading.template'].search(domain_search_pkwt, limit=1, order='nilai_max_alw_pkwt desc')
			
			domain_search_ppkwt = self._get_domain_grading('alw_ppkwt', rec.persen_ppkwt)
			rec.grade_ppkwt_id = self.env['grading.template'].search(domain_search_ppkwt, limit=1, order='nilai_max_alw_ppkwt desc')

			domain_search_resign = self._get_domain_grading('alw_resign', rec.persen_kesalahan_resign)
			rec.grade_kesalahan_resign_id = self.env['grading.template'].search(domain_search_resign, limit=1, order='nilai_max_alw_resign desc')

			rec.potongan_absen = rec.grade_absen_id.potongan_absen
			
			# domain_search_avg = self._get_domain_grading('avg', rec.average_alw)
			# rec.grade_average_id = self.env['grading.template'].search(domain_search_avg, limit=1, order='nilai_max_alw_resign desc')

	def _get_domain_grading(self, key, field):
		nilai_min = f'nilai_min_{key}'
		nilai_max = f'nilai_max_{key}'
		return [(nilai_min, '<=', field), (nilai_max, '>', field)]	
