from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError


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
	average_ro = fields.Float(string='Average RO')
	average_alw = fields.Float(string='Average ALW')
	grading_ro_id = fields.Many2one(comodel_name='grading.template', string='Grading RO')
	grading_alw_id = fields.Many2one(comodel_name='grading.template', string='Grading ALW')
	insentif_g_ro = fields.Float(string='Insentif G RO')
	insentif_g_alw = fields.Float(string='Insentif G ALW')
	total_insentif = fields.Float(string='Total')
	penyesuaian = fields.Float(string='Penyesuaian Kadiv')

# %A. RO	%A.ALW	Grading RO	Grading ALW	Insentif G RO	Insentif G ALW	Total	Penyesuaian Kadiv  Sebelumnya



	employee_alw_kpi_line = fields.One2many(comodel_name='employee.alw.kpi', inverse_name='employee_kpi_batch_id', string='ALW KPI')
	employee_kpi_line = fields.One2many(comodel_name='employee.kpi', inverse_name='employee_kpi_batch_id', string='RO KPI')

	alw_monthly_kpi_line = fields.One2many(comodel_name='alw.monthly.kpi.line', inverse_name='employee_kpi_batch_id', string='ALW Monthly KPI')
	employee_monthly_kpi_line = fields.One2many(comodel_name='employee.monthly.kpi.line', inverse_name='employee_kpi_batch_id', string='RO Monthly KPI')

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
		params = self.env['ir.config_parameter'].sudo()
		ro_employee_ids = self.kro_id.child_ids.filtered(lambda e:e.job_id.id == int(params.get_param('mum_kpi.default_job_ro_id')))
		alw_employee_ids = self.kro_id.child_ids.filtered(lambda e:e.job_id.id == int(params.get_param('mum_kpi.default_job_alw_id')))
		
		# values utk data penilaian bulanan per karyawan
		monthly_kpi_line_values = [(Command.create({
			'name' : f'{month.name} {self.tgl_dibuat.strftime("%Y")}',
			'month_id' : month.id,
			'employee_kpi_batch_id' : self.id,
		})) for month in self.month_ids]
		
		# values untuk KPI per karyawan
		ro_employee_kpi_values = [{
				'employee_kpi_batch_id' : self.id,
				'employee_id' : employee.id,
				'employee_monthly_kpi_line' : monthly_kpi_line_values
			} for employee in ro_employee_ids]
		
		alw_kpi_values = [{
			'employee_kpi_batch_id' : self.id,
			'employee_id' : employee.id,
			'alw_monthly_kpi_line' : monthly_kpi_line_values,
		} for employee in alw_employee_ids]

		ro_employee_kpi_ids = self.env['employee.kpi'].create(ro_employee_kpi_values)
		alw_employee_kpi_ids = self.env['employee.alw.kpi'].create(alw_kpi_values)
		return ro_employee_kpi_ids, alw_employee_kpi_ids
	
	def _find_monthly_grading(self, monthly_ids, tgl_dibuat):
		monthly_grading_ids = self.env['monthly.grading'].search([('month_id', 'in', monthly_ids.ids), ('tahun', '=', tgl_dibuat.strftime('%Y'))])
		# cek apakah ada grading bulanan yang belum terbentuk, jika ada maka buat grading bulanan dan masukkan ke dalam monthly_grading_ids
		# sintaks symmetric_difference adalah built-in function tipe data set, yg berfungsi utk mencari perbedaan dari 2 dataset
		monthly_grading_to_create = list(set(monthly_ids.ids).symmetric_difference(set(monthly_grading_ids.month_id.ids)))
		if monthly_grading_to_create:
			grading_template_values = [(Command.create({
				'grade_template_id' : template.id,
				'grade' : template.grade,
				'nilai_min_ro' : template.nilai_min_ro,
				'nilai_max_ro' : template.nilai_max_ro,
				'nilai_min_alw_resign' : template.nilai_min_alw_resign,
				'nilai_max_alw_resign' : template.nilai_max_alw_resign,
				'nilai_min_alw_incomplete_data' : template.nilai_min_alw_incomplete_data,
				'nilai_max_alw_incomplete_data' : template.nilai_max_alw_incomplete_data,
				'nilai_min_alw_pkwt' : template.nilai_min_alw_pkwt,
				'nilai_max_alw_pkwt' : template.nilai_max_alw_pkwt,
				'nilai_min_alw_ppkwt' : template.nilai_min_alw_ppkwt,
				'nilai_max_alw_ppkwt' : template.nilai_max_alw_ppkwt,
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
		ro_employee_kpi_ids, alw_employee_kpi_ids = self._create_employee_kpi()
		# 1. periksa apakah rekap grading bulanan sudah ada? gunakan method find_monthly_grading(month_id, year)
		monthly_grading_ids = self._find_monthly_grading(self.month_ids, self.tgl_dibuat)
		ro_kpi_grading_ids = monthly_grading_ids._create_employee_kpi_grading(ro_employee_kpi_ids.employee_monthly_kpi_line)
		return self.write({'state' : 'in_progress'})
	
	# def _create_
	
	def button_submit(self):
		# print(any(line.absen == 0 or line.more == 0 for line in self.employee_kpi_line))
		if any(line.absen == 0 or line.more == 0 for line in self.employee_kpi_line):
			raise ValidationError(_("Kolom Absen dan kolom More RO tidak boleh berisi 0"))
		if any(line.absen == 0 for line in self.employee_alw_kpi_line):
			raise ValidationError(_("Kolom Absen ALW tidak boleh berisi 0"))
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

