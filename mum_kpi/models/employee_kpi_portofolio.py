from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError

class EmployeeKpiPortofolio(models.Model):
	_name = 'employee.portofolio.kpi'
	_inherit = ['mail.activity.mixin', 'mail.thread']
	_description = 'Employee KPI Portofolio'

	name = fields.Char(string='Nomor Batch')
	tgl_dibuat = fields.Date(string='Tanggal Dibuat', default=lambda self:fields.Date.context_today(self))
	tahun = fields.Char(string='Tahun')
	periode_id = fields.Many2one(comodel_name='kpi.periode', string='Periode Insentif')
	kpi_mekaar_batch_id = fields.Many2one(comodel_name='kpi.mekaar.batch', string='KPI Mekaar Batch')
	month_ids = fields.Many2many(comodel_name='res.month', string='Bulan', related='periode_id.month_ids')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Responsible', default=lambda s:s.env.user.employee_id)
	employee_manager_id = fields.Many2one(comodel_name='hr.employee', string='Kadiv', related='employee_id.parent_id')
	state = fields.Selection(string='State', selection=[
		('draft', 'Draft'), 
		('in_progress', 'In Progress'),
		('approval_1', 'Approval 1'),
		('done', 'Done'),
		('cancel', 'Cancel')], default='draft', copy=False, tracking=True)
	
	kpi_sebelumnya_id = fields.Many2one(comodel_name='employee.portofolio.kpi', string='KPI Sebelumnya')
	
	total_insentif = fields.Float(string='Total Insentif', compute='_compute_total_insentif')
	total_insentif_penyesuaian = fields.Float(string='Total Penyesuaian', compute='_compute_total_insentif')
	total_insentif_sebelumnya = fields.Float(string='Total Insentif Sebelumnya', compute='_compute_total_insentif')

	company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda self:self.env.company)
	employee_portofolio_kpi_line = fields.One2many(comodel_name='employee.portofolio.kpi.line', inverse_name='employee_portofolio_kpi_id', string='Portofolio KPI Line')

	# CRUD Method
	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('employee.portofolio.kpi.seq', fields.Date.to_date(vals.get('tgl_dibuat')))
		vals['tahun'] = fields.Date.to_date(vals.get('tgl_dibuat')).strftime("%Y")
		return super().create(vals)
	
	# Compute Method
	@api.depends(
		'employee_portofolio_kpi_line.total_insentif',
		'employee_portofolio_kpi_line.insentif_periode_sebelumnya',
		'employee_portofolio_kpi_line.penyesuaian'
	)
	def _compute_total_insentif(self):
		for rec in self:
			rec.total_insentif = sum(x.total_insentif for x in rec.employee_portofolio_kpi_line)
			rec.total_insentif_penyesuaian = sum(x.penyesuaian for x in rec.employee_portofolio_kpi_line)
			rec.total_insentif_sebelumnya = sum(x.insentif_periode_sebelumnya for x in rec.employee_portofolio_kpi_line)


	# Bussiness Logic 
	def _create_employee_kpi(self):
		params = self.env['ir.config_parameter'].sudo()
		ro_employee_ids = self.employee_id.child_ids.filtered(lambda e:e.job_id.id == int(params.get_param('mum_kpi.default_job_ro_id')))

		# values utk data penilaian bulanan per karyawan
		# 1. periksa apakah kpi mekaar batch sudah ada? gunakan method _find_mekaar_batch()
		# 2. periksa apakah rekap grading bulanan sudah ada? gunakan method find_monthly_grading(month_id, year)
		# 3. sisipkan field kpi_mekaar_batch_id ke dalam self.kpi_mekaar_batch_id
		# 4. berikan nilai kpi sebelumnya per karyawan.
		kpi_mekaar_batch_id = self.env['kpi.mekaar.batch']._find_mekaar_batch(self.periode_id, self.tahun, self.tgl_dibuat)
		self.kpi_mekaar_batch_id = kpi_mekaar_batch_id.id
		monthly_grading_ids = self.env['monthly.grading']._find_monthly_grading(self.month_ids, self.periode_id, self.tgl_dibuat)
		monthly_grading_ids.write({'kpi_mekaar_batch_id' : self.kpi_mekaar_batch_id.id})
		monthly_kpi_line_values = []
		sequence = 0
		for month in self.month_ids:
			sequence += 1
			monthly_kpi_line_values.append((Command.create({
			'sequence' : sequence,
			'name' : f'{month.name} {self.tgl_dibuat.strftime("%Y")}',
			'month_id' : month.id,
			'monthly_grading_id' : monthly_grading_ids.filtered(lambda m:m.month_id == month).id,
			'employee_portofolio_kpi_id' : self.id,
		})))
		
		
		# values untuk KPI per karyawan
		
		ro_employee_kpi_values = [{
				'employee_portofolio_kpi_id' : self.id,
				# 'kpi_mekaar_batch_id' : kpi_mekaar_batch_id.id,
				'employee_id' : employee.id,
				'employee_kpi_line_sebelumnya_id' : self.kpi_sebelumnya_id.employee_portofolio_kpi_line.filtered(lambda l:l.employee_id == employee).id,
				'portofolio_monthly_line' : monthly_kpi_line_values
			} for employee in ro_employee_ids]

		ro_employee_kpi_ids = self.env['employee.portofolio.kpi.line'].create(ro_employee_kpi_values)
		return ro_employee_kpi_ids

	# Button Actions 
	def button_confirm(self):
		self.kpi_sebelumnya_id = self.search([('id', '!=', self.id), ('employee_id', '=', self.employee_id.id)], limit=1, order='tahun desc, periode_id desc').id
		if self.kpi_sebelumnya_id.state != 'done':
			raise ValidationError(_(f"Periode {self.kpi_sebelumnya_id.name} belum terselesaikan, harap selesaikan terlebih dahulu."))
		portofolio_line_ids = self._create_employee_kpi()
		return self.write({'state' : 'in_progress'})
	
	def button_submit(self):

		return self.write({'state' : 'done'})
	
	def button_draft(self):

		return self.write({'state' : 'draft'})
	
	def action_show_details(self):
		self.ensure_one()
		tree_view = self.env.ref('mum_kpi.employee_portofolio_kpi_line_view_tree')
		form_view = self.env.ref('mum_kpi.employee_portofolio_kpi_line_view_form')
		# pivot_view = self.env.ref('mum_kpi.employee_kpi_view_pivot')
		return {
			'name': _('Detail KPI Bulanan'),
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'employee.portofolio.kpi.line',
			'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
			'view_id': tree_view.id,
			'target': 'self',
			'domain' : [('id', 'in', self.employee_portofolio_kpi_line.ids)]
		}
	
class EmployeePortofolioKpiLine(models.Model):
	_name = 'employee.portofolio.kpi.line'
	_description = 'Employee Portofolio KPI Line'
	_rec_name = 'employee_id'

	# name = fields.Char(string='Name')
	
	employee_portofolio_kpi_id = fields.Many2one(comodel_name='employee.portofolio.kpi', string='Portofolio KPI')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan')
	total_kekurangan = fields.Float(string='Kekurangan', compute='_compute_pencapaian_karyawan')
	total_incomplete_data = fields.Float(string='Incomplete Data', compute='_compute_pencapaian_karyawan')
	total_sla = fields.Integer(string='SLA', compute='_compute_pencapaian_karyawan')
	# total_absen = fields.Integer(string='Absen')
	# total_more = fields.Integer(string='More')
	
	grade_incomplete_data_id = fields.Many2one(comodel_name='grading.template', string='Grade Incomplete Data', compute='_compute_pencapaian_karyawan')
	grade_kekurangan_id = fields.Many2one(comodel_name='grading.template', string='Grade Kekurangan', compute='_compute_pencapaian_karyawan')
	grade_sla_id = fields.Many2one(comodel_name='grading.template', string='Grade SLA', compute='_compute_pencapaian_karyawan')
	# grade_absen_id = fields.Many2one(comodel_name='grading.template', string='Grade Absen')
	# grade_more_id = fields.Many2one(comodel_name='grading.template', string='Grade More')
	
	insentif_kekurangan = fields.Float(string='Insentif Kekurangan', related='grade_kekurangan_id.insentif_portofolio_kekurangan', store=True)
	insentif_incomplete_data = fields.Float(string='Insentif Incomplete Data', related='grade_incomplete_data_id.insentif_portofolio_incomplete_data', store=True)
	insentif_sla = fields.Float(string='Insentif SLA', related='grade_sla_id.insentif_portofolio_sla', store=True)
	total_insentif_more = fields.Float(string='Insentif More', compute="_compute_total_insentif", store=True)
	total_potongan_absen = fields.Float(string='Potongan Absen', compute="_compute_total_insentif", store=True)

	employee_kpi_line_sebelumnya_id = fields.Many2one(comodel_name='employee.portofolio.kpi.line', string='KPI RO Sebelumnya')

	total_insentif = fields.Float(string='Total Insentif', compute='_compute_total_insentif')
	insentif_periode_sebelumnya = fields.Float(string='Insentif Sebelumnya', related='employee_kpi_line_sebelumnya_id.penyesuaian', store=True)
	selisih = fields.Float(string='Selisih Insentif', compute='_compute_total_insentif', store=True)
	penyesuaian = fields.Float(string='Penyesuaian Insentif')
	alasan_penyesuaian = fields.Char(string='Alasan Penyesuaian')
	
	state = fields.Selection(string='State', related='employee_portofolio_kpi_id.state', store=True)
	
	portofolio_monthly_line = fields.One2many(comodel_name='employee.portofolio.kpi.monthly.line', inverse_name='employee_portofolio_line_id', string='Portofolio Monthly Line')
	company_id = fields.Many2one(comodel_name='res.company', string='Company', related='employee_portofolio_kpi_id.company_id', store=True)

	@api.depends(
		'portofolio_monthly_line.absen',
		'portofolio_monthly_line.more',
		'insentif_kekurangan',
		'insentif_incomplete_data',
		'insentif_sla',
		'insentif_periode_sebelumnya'
	)
	def _compute_total_insentif(self):
		for rec in self:
			rec.total_potongan_absen = sum(x.potongan_absen for x in rec.portofolio_monthly_line)
			rec.total_insentif_more = sum(x.insentif_more for x in rec.portofolio_monthly_line)
			rec.total_insentif = rec.insentif_kekurangan + rec.insentif_incomplete_data + rec.insentif_sla + rec.total_insentif_more + rec.total_potongan_absen
			rec.selisih = rec.total_insentif - rec.insentif_periode_sebelumnya

	@api.depends(
		'portofolio_monthly_line.kekurangan',
		'portofolio_monthly_line.incomplete_data',
		'portofolio_monthly_line.sla'
		)
	def _compute_pencapaian_karyawan(self):
		# kpi_grading_ids = self.monthly_grading_id.resume_kpi_grading_ids
		
		for rec in self:
			# Rekrutmen = rekrutmen / formasi
			# maintain = average(pemenuhan / pemenuhan periode)
			# tl = tl / formasi kurangx
			rec.total_kekurangan = sum(line.kekurangan for line in rec.portofolio_monthly_line)
			rec.total_incomplete_data = sum(line.incomplete_data for line in rec.portofolio_monthly_line)
			rec.total_sla = sum(line.sla for line in rec.portofolio_monthly_line)
			
			# Hitung Grading
			domain_search_grade_kekurangan = self._get_domain_grading('kekurangan', rec.total_kekurangan)
			rec.grade_kekurangan_id = self.env['grading.template'].search(domain_search_grade_kekurangan, limit=1, order='nilai_max_portofolio_kekurangan desc')

			domain_search_grade_incomplete_data = self._get_domain_grading('incomplete_data', rec.total_incomplete_data)
			rec.grade_incomplete_data_id = self.env['grading.template'].search(domain_search_grade_incomplete_data, limit=1, order='nilai_max_portofolio_incomplete_data desc')

			domain_search_grade_sla = self._get_domain_grading('sla', rec.total_sla)
			rec.grade_sla_id = self.env['grading.template'].search(domain_search_grade_sla, limit=1, order='nilai_max_portofolio_sla desc')

	def _get_domain_grading(self, key, field):
		nilai_min = f'nilai_min_portofolio_{key}'
		nilai_max = f'nilai_max_portofolio_{key}'
		return [(nilai_min, '<=', field), (nilai_max, '>', field)]

	def action_show_details(self):
		self.ensure_one()
		view = self.env.ref('mum_kpi.employee_portofolio_kpi_line_view_form')
		return {
			'name': _('Detail KPI %s'%self.employee_id.name),
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': self._name,
			'views': [(view.id, 'form')],
			'view_id': view.id,
			'target': 'self',
			'res_id': self.id,
		}

class EmployeePortofolioKpiMonthlyLine(models.Model):
	_name = 'employee.portofolio.kpi.monthly.line'
	_description = 'Employee Portofolio Monthly Line'
	
	name = fields.Char(string='Periode')
	sequence = fields.Integer(string='Sequence')
	monthly_grading_id = fields.Many2one(comodel_name='monthly.grading', string='Monthly Grading')
	month_id = fields.Many2one(comodel_name='res.month', string='Month')
	employee_portofolio_kpi_id = fields.Many2one(comodel_name='employee.portofolio.kpi', string='Portofolio KPI')
	employee_portofolio_line_id = fields.Many2one(comodel_name='employee.portofolio.kpi.line', string='Portofolio Line')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan')
	kekurangan = fields.Integer(string='Kekurangan')
	incomplete_data = fields.Float(string='Incomplete Data')
	sla = fields.Integer(string='SLA')
	
	absen = fields.Integer(string='Keterlambatan (Menit)')
	tidak_masuk = fields.Integer(string='Tidak Masuk (Hari)')
	more = fields.Integer(string='MORE')
	grade_absensi_id = fields.Many2one(comodel_name='grading.template', string='Grade Absen', compute='_compute_absen_more', store=True)
	grade_more_id = fields.Many2one(comodel_name='grading.template', string='Grade More', compute='_compute_absen_more', store=True)
	potongan_absen = fields.Float(string='Potongan Absen', related='grade_absensi_id.potongan_absen', store=True)
	insentif_more = fields.Float(string='Insentif MORE', related='grade_more_id.insentif_more', store=True)
	state = fields.Selection(string='State', related='employee_portofolio_kpi_id.state', store=True)
	company_id = fields.Many2one(comodel_name='res.company', string='Company', related='employee_portofolio_kpi_id.company_id', store=True)

	@api.depends('absen', 'more')
	def _compute_absen_more(self):
		for rec in self:
			domain_search_absen = [('nilai_min_absen', '<=', rec.absen), ('nilai_max_absen', '>', rec.absen)]
			rec.grade_absensi_id = self.env['grading.template'].search(domain_search_absen, limit=1, order='nilai_max_absen desc')

			domain_search_grade_more = [('nilai_min_more', '<=', rec.more), ('nilai_max_more', '>', rec.more)]
			rec.grade_more_id = self.env['grading.template'].search(domain_search_grade_more, limit=1, order='nilai_max_more desc')

			# rec.potongan_absen = rec.grade_absensi_id.potongan_absen