from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError
import random

# class EmployeeKpiKro(models.Model):
# 	_name = 'employee.kpi.kro'

class EmployeeKpiKro(models.Model):
	_name = 'employee.kro.kpi'
	_inherit = ['mail.activity.mixin', 'mail.thread']
	_description = 'Insentif RO'
	_check_company_auto = True

	name = fields.Char(string='Name')
	tgl_dibuat = fields.Date(string='Tanggal Dibuat', default=lambda self:fields.Date.context_today(self))
	tahun = fields.Char(string='Tahun')
	periode_id = fields.Many2one(comodel_name='kpi.periode', string='Periode Insentif')
	kpi_mekaar_batch_id = fields.Many2one(comodel_name='kpi.mekaar.batch', string='KPI Mekaar Batch')
	month_ids = fields.Many2many(comodel_name='res.month', string='Bulan')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='KRO', default=lambda s:s.env.user.employee_id)
	employee_manager_id = fields.Many2one(comodel_name='hr.employee', string='Kabag', related='employee_id.parent_id')
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
	alasan_penyesuaian = fields.Char(string='Alasan Penyesuaian')
	more = fields.Integer(string='MORE', compute='_compute_total_ro_more')
	absen = fields.Integer(string='Keterlambatan (Menit)')
	tidak_masuk = fields.Integer(string='Tidak Masuk (Hari)')

	grade_absensi_id = fields.Many2one(comodel_name='grading.template', string='Grade Absensi')
	potongan_absen = fields.Float(string='Potongan Absensi')

	total_insentif_ro = fields.Float(string='Total Insentif', compute='_compute_total')
	total_insentif_sebelumnya_ro = fields.Float(string='Total Insentif Sebelumnya' , compute='_compute_total')
	total_penyesuaian_ro = fields.Float(string='Total Penyesuaian', compute='_compute_total')
	total_insentif_alw = fields.Float(string='Total Insentif', compute='_compute_total')
	total_insentif_sebelumnya_alw = fields.Float(string='Total Insentif Sebelumnya', compute='_compute_total')
	total_penyesuaian_alw = fields.Float(string='Total Penyesuaian', compute='_compute_total')
	
	kpi_sebelumnya_id = fields.Many2one(comodel_name='employee.kro.kpi', string='KPI Sebelumnya')

	employee_alw_kpi_line = fields.One2many(comodel_name='employee.alw.kpi', inverse_name='employee_kro_kpi_id', string='ALW KPI')
	employee_alw_kpi_line_count = fields.Integer(string='ALW Count', compute='_compute_kpi_line_count')
	employee_kpi_line = fields.One2many(comodel_name='employee.ro.kpi', inverse_name='employee_kro_kpi_id', string='RO KPI')
	employee_kpi_line_count = fields.Integer(string='RO Count', compute='_compute_kpi_line_count')
	alw_monthly_kpi_line = fields.One2many(comodel_name='alw.monthly.kpi.line', inverse_name='employee_kro_kpi_id', string='ALW Monthly KPI')
	employee_monthly_kpi_line = fields.One2many(comodel_name='employee.monthly.kpi.line', inverse_name='employee_kro_kpi_id', string='RO Monthly KPI')

	def _compute_kpi_line_count(self):
		for rec in self:
			rec.employee_kpi_line_count = len(rec.employee_kpi_line)
			rec.employee_alw_kpi_line_count = len(rec.employee_alw_kpi_line)
	
	# @api.depends('employee_kpi_line.more')
	def _compute_total_ro_more(self):
		for rec in self:
			rec.more = sum(x.more for x in rec.employee_kpi_line) 

	@api.depends(
		'employee_alw_kpi_line',
		'employee_kpi_line'
	)
	def _compute_total(self):
		for rec in self:
			rec.total_insentif_ro = sum(x.total_insentif for x in rec.employee_kpi_line)
			rec.total_insentif_sebelumnya_ro = sum(x.insentif_sebelumnya for x in rec.employee_kpi_line)
			rec.total_penyesuaian_ro = sum(x.penyesuaian for x in rec.employee_kpi_line)
			rec.total_insentif_alw = sum(x.total_insentif for x in rec.employee_alw_kpi_line)
			rec.total_insentif_sebelumnya_alw = sum(x.insentif_sebelumnya for x in rec.employee_alw_kpi_line)
			rec.total_penyesuaian_alw = sum(x.penyesuaian for x in rec.employee_alw_kpi_line)

	@api.model
	def create(self, vals):
		# CODE HERE
		vals['name'] = self.env['ir.sequence'].next_by_code('employee.kro.kpi.seq', fields.Date.to_date(vals.get('tgl_dibuat')))
		vals['tahun'] = fields.Date.to_date(vals.get('tgl_dibuat')).strftime("%Y")
		return super(EmployeeKpiKro, self).create(vals)
	
	# Lanjutkan yang ini.
	# @api.depends('employee_kpi_line.average', 'employee_alw_kpi_line.average_alw', 'absen')
	def _compute_average_grade(self):
		for rec in self:
			total_ro = len(rec.employee_kpi_line)
			total_alw = len(rec.employee_alw_kpi_line)
			rec.average_ro = rec.average_alw = 0
			if total_ro:
				rec.average_ro = sum(l.average for l in rec.employee_kpi_line) / total_ro
			if total_alw:
				rec.average_alw = sum(l.average_alw for l in rec.employee_alw_kpi_line) / total_alw

			domain_search_avg_ro = self._get_domain_grading('ro_avg', rec.average_ro)
			rec.grading_ro_id = self.env['grading.template'].search(domain_search_avg_ro, limit=1, order='nilai_max_ro_avg desc')
			domain_search_avg_alw = self._get_domain_grading('alw_avg', rec.average_alw)
			rec.grading_alw_id = self.env['grading.template'].search(domain_search_avg_alw, limit=1, order='nilai_max_alw_avg desc')
			domain_search_absen_kro = self._get_domain_grading('absen', rec.absen)
			rec.grade_absensi_id = self.env['grading.template'].search(domain_search_absen_kro, limit=1, order='nilai_max_absen desc')

			rec.potongan_absen = rec.grade_absensi_id.potongan_absen
			rec.insentif_g_ro = rec.grading_ro_id.insentif_kro_ro
			rec.insentif_g_alw = rec.grading_alw_id.insentif_kro_alw
			rec.total_insentif = rec.insentif_g_ro + rec.insentif_g_alw + rec.potongan_absen

			
	def _get_domain_grading(self, key, field):
		nilai_min = f'nilai_min_{key}'
		nilai_max = f'nilai_max_{key}'
		return [(nilai_min, '<=', field), (nilai_max, '>', field)]
	
	@api.onchange('employee_id')
	def _onchange_kro_id(self):
		self.user_approval_1 = self.employee_id.parent_id.user_id.id
		self.user_approval_2 = self.employee_id.parent_id.parent_id.user_id.id
	
	@api.onchange('periode_id')
	def _onchange_periode(self):
		self.month_ids = self.periode_id.month_ids
	
	def _create_employee_kpi(self):
		params = self.env['ir.config_parameter'].sudo()
		ro_employee_ids = self.employee_id.child_ids.filtered(lambda e:e.job_id.id == int(params.get_param('mum_kpi.default_job_ro_id')))
		alw_employee_ids = self.employee_id.child_ids.filtered(lambda e:e.job_id.id == int(params.get_param('mum_kpi.default_job_alw_id')))
		
		# values utk data penilaian bulanan per karyawan
		# 1. periksa apakah kpi mekaar batch sudah ada? gunakan method _find_mekaar_batch()
		# 2. periksa apakah rekap grading bulanan sudah ada? gunakan method find_monthly_grading(month_id, year)
		# 3. sisipkan field kpi_mekaar_batch_id ke dalam self.kpi_mekaar_batch_id
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
			'employee_kro_kpi_id' : self.id,
		})))
		
		
		# values untuk KPI per karyawan
		ro_employee_kpi_values = [{
				'employee_kro_kpi_id' : self.id,
				'kpi_mekaar_batch_id' : kpi_mekaar_batch_id.id,
				'employee_id' : employee.id,
				'employee_kpi_line_sebelumnya_id' : self.kpi_sebelumnya_id.employee_kpi_line.filtered(lambda l:l.employee_id == employee).id,
				'employee_monthly_kpi_line' : monthly_kpi_line_values
			} for employee in ro_employee_ids]
		
		alw_kpi_values = [{
			'employee_kro_kpi_id' : self.id,
			'kpi_mekaar_batch_id' : kpi_mekaar_batch_id.id,
			'employee_id' : employee.id,
			'employee_kpi_line_sebelumnya_id' : self.kpi_sebelumnya_id.employee_alw_kpi_line.filtered(lambda l:l.employee_id == employee).id,
			'alw_monthly_kpi_line' : monthly_kpi_line_values,
		} for employee in alw_employee_ids]

		ro_employee_kpi_ids = self.env['employee.ro.kpi'].create(ro_employee_kpi_values)
		alw_employee_kpi_ids = self.env['employee.alw.kpi'].create(alw_kpi_values)
		return ro_employee_kpi_ids, alw_employee_kpi_ids
	
	def _find_mekaar_batch(self, periode_id, tahun):
		mekaar_batch_id = self.env['kpi.mekaar.batch'].sudo().search([('periode_id', '=', periode_id.id), ('tahun', '=', tahun)])
		if not mekaar_batch_id:
			mekaar_batch_id = self.env['kpi.mekaar.batch'].sudo().create({'periode_id' : periode_id.id, 'tahun' : tahun, 'tgl_dibuat' : self.tgl_dibuat})
		
		return mekaar_batch_id
	
	def _find_monthly_grading(self, monthly_ids, tgl_dibuat):
		monthly_grading_ids = self.env['monthly.grading'].search([('month_id', 'in', monthly_ids.ids), ('tahun', '=', tgl_dibuat.strftime('%Y'))])
		# cek apakah ada grading bulanan yang belum terbentuk, jika ada maka buat grading bulanan dan masukkan ke dalam monthly_grading_ids
		# sintaks symmetric_difference adalah built-in function tipe data set, yg berfungsi utk mencari perbedaan dari 2 dataset
		monthly_grading_to_create = list(set(monthly_ids.ids).symmetric_difference(set(monthly_grading_ids.month_id.ids)))
		if monthly_grading_to_create:
			grading_template_values = [(Command.create({
				'grade_template_id' : template.id,
				'kpi_mekaar_batch_id' : self.kpi_mekaar_batch_id.id,
				'grade' : template.grade,
			})) for template in self.env['grading.template'].search([])]
			values = [{
				'periode_id' : self.periode_id.id,
				'month_id' : monthly_grading,
				'tahun' : self.tgl_dibuat.strftime("%Y"),
				'resume_kpi_grading_ids' : grading_template_values,
			} for monthly_grading in monthly_grading_to_create]
			created_monthly_grading_ids = self.env['monthly.grading'].create(values)
			# pertanyaan, apakah tanda |= pada odoo dapat diartikan menambahkan recordset yg baru ke recordset yg sudah ada ? BENARR
			monthly_grading_ids |= created_monthly_grading_ids
			
		return monthly_grading_ids
	
	def button_confirm(self):
		self.kpi_sebelumnya_id = self.search([('id', '!=', self.id), ('employee_id', '=', self.employee_id.id)], limit=1, order='tahun desc, periode_id desc').id
		if self.kpi_sebelumnya_id.state != 'done':
			raise ValidationError(_(f"Periode {self.kpi_sebelumnya_id.name} belum terselesaikan, harap selesaikan terlebih dahulu."))
		ro_employee_kpi_ids, alw_employee_kpi_ids = self._create_employee_kpi()
		return self.write({'state' : 'in_progress'})
	
	def button_inprogress(self):
		return self.write({'state' : 'in_progress'})
	
	def button_submit(self):
		# print(any(line.absen == 0 or line.more == 0 for line in self.employee_kpi_line))
		self.employee_alw_kpi_line.action_confirm()
		self._compute_average_grade()
		return self.write({'state' : 'approval_1'})
	
	def _compute_show_approval_button(self):
		self.show_approval_button = False
		if (self.state == 'approval_1' and self.env.user == self.user_approval_1) or \
			  (self.state == 'approval_2' and self.env.user == self.user_approval_2) or self.user_has_groups('base.group_system'):
			self.show_approval_button = True

	def button_approve_1(self):
		return self.write({'state' : 'approval_2'})
	
	def button_done(self):
		return self.write({'state' : 'done'})
	
	def button_cancel(self):
		return self.write({'state' : 'cancel'})
	
	def action_show_details_ro(self):
		self.ensure_one()
		tree_view = self.env.ref('mum_kpi.employee_kpi_view_tree')
		form_view = self.env.ref('mum_kpi.employee_kpi_view_form')
		# pivot_view = self.env.ref('mum_kpi.employee_kpi_view_pivot')
		return {
			'name': _('Detail KPI RO'),
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'employee.ro.kpi',
			'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
			'view_id': tree_view.id,
			'target': 'self',
			'domain' : [('id', 'in', self.employee_kpi_line.ids)]
		}

	def action_show_details_alw(self):
		self.ensure_one()
		tree_view = self.env.ref('mum_kpi.employee_alw_kpi_view_tree')
		form_view = self.env.ref('mum_kpi.employee_alw_kpi_view_form')
		return {
			'name': _('Detail KPI ALW'),
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'employee.alw.kpi',
			'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
			'view_id': tree_view.id,
			'target': 'self',
			'domain' : [('id', 'in', self.employee_alw_kpi_line.ids)]
		}
	
	def fill_employee_monthly_kpi_line(self):
		values = []
		for line in self.employee_monthly_kpi_line:
			line.absen = random.randint(20,26)
			line.more = random.randint(300,400)
			line.cabang = random.randint(30,35)
			line.formasi = random.randint(400,500)
			line.aktif = random.randint(300,450)
			line.resign = random.randint(20,40)
			line.rekrutmen = random.randint(10,30)
			line.tl = random.randint(10,30)


	def fill_alw_monthly_kpi_line(self):
		for line in self.alw_monthly_kpi_line:
			line.absen = random.randint(20,26)
			line.karyawan_terakhir = random.randint(500,800)
			line.resign = random.randint(5,30)
			line.perp_kontrak = random.randint(5,30)
			line.incomplete_data = random.randint(20,int(line.karyawan_terakhir/4))
			line.pkwt = random.randint(0, int(line.karyawan_terakhir/4))
			line.ppkwt = random.randint(0, int(line.perp_kontrak/4))
			line.kesalahan_resign = random.randint(0,int(line.resign/4))

	def auto_fill_random_values(self):
		# random.randint(0,200)
		alw_monthly_kpi_line_values = self.fill_alw_monthly_kpi_line()
		employee_monthly_kpi_line_values = self.fill_employee_monthly_kpi_line()