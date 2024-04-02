from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError
import random


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
	average_ro = fields.Float(string='Average RO', compute='_compute_average_grade', store=True, precompute=True, tracking=True)
	average_alw = fields.Float(string='Average ALW', compute='_compute_average_grade', store=True, precompute=True, tracking=True)
	grading_ro_id = fields.Many2one(comodel_name='grading.template', string='Grading RO', compute='_compute_average_grade', store=True, precompute=True)
	grading_alw_id = fields.Many2one(comodel_name='grading.template', string='Grading ALW', compute='_compute_average_grade', store=True, precompute=True)
	insentif_g_ro = fields.Float(string='Insentif G RO', compute='_compute_average_grade', store=True, )
	insentif_g_alw = fields.Float(string='Insentif G ALW', compute='_compute_average_grade', store=True, )
	total_insentif = fields.Float(string='Total', compute='_compute_average_grade', store=True,)
	penyesuaian = fields.Float(string='Penyesuaian Kadiv')
	alasan_penyesuaian = fields.Char(string='Alasan Penyesuaian')

	employee_alw_kpi_line = fields.One2many(comodel_name='employee.alw.kpi', inverse_name='employee_kpi_batch_id', string='ALW KPI')
	employee_alw_kpi_line_count = fields.Integer(string='ALW Count', compute='_compute_kpi_line_count')
	employee_kpi_line = fields.One2many(comodel_name='employee.kpi', inverse_name='employee_kpi_batch_id', string='RO KPI')
	employee_kpi_line_count = fields.Integer(string='RO Count', compute='_compute_kpi_line_count')
	alw_monthly_kpi_line = fields.One2many(comodel_name='alw.monthly.kpi.line', inverse_name='employee_kpi_batch_id', string='ALW Monthly KPI')
	employee_monthly_kpi_line = fields.One2many(comodel_name='employee.monthly.kpi.line', inverse_name='employee_kpi_batch_id', string='RO Monthly KPI')

	def _compute_kpi_line_count(self):
		for rec in self:
			rec.employee_kpi_line_count = len(rec.employee_kpi_line)
			rec.employee_alw_kpi_line_count = len(rec.employee_alw_kpi_line)

	@api.model
	def create(self, vals):
		# CODE HERE
		vals['name'] = self.env['ir.sequence'].next_by_code('employee.kpi.batch.seq', fields.Date.to_date(vals.get('tgl_dibuat')))
		return super(EmployeeKpiBatch, self).create(vals)
	
	# Lanjutkan yang ini.
	@api.depends('employee_kpi_line.average', 'employee_alw_kpi_line.average_alw')
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

			rec.insentif_g_ro = rec.grading_ro_id.insentif_kro_ro
			rec.insentif_g_alw = rec.grading_alw_id.insentif_kro_alw
			rec.total_insentif = rec.insentif_g_ro + rec.insentif_g_alw

			
	def _get_domain_grading(self, key, field):
		nilai_min = f'nilai_min_{key}'
		nilai_max = f'nilai_max_{key}'
		return [(nilai_min, '<=', field), (nilai_max, '>', field)]
	
	@api.onchange('kro_id')
	def _onchange_kro_id(self):
		self.user_approval_1 = self.kro_id.parent_id.user_id.id
		self.user_approval_2 = self.kro_id.parent_id.parent_id.user_id.id
	
	@api.onchange('periode_id')
	def _onchange_periode(self):
		self.month_ids = self.periode_id.month_ids
	
	def _create_employee_kpi(self):
		params = self.env['ir.config_parameter'].sudo()
		ro_employee_ids = self.kro_id.child_ids.filtered(lambda e:e.job_id.id == int(params.get_param('mum_kpi.default_job_ro_id')))
		alw_employee_ids = self.kro_id.child_ids.filtered(lambda e:e.job_id.id == int(params.get_param('mum_kpi.default_job_alw_id')))
		
		# values utk data penilaian bulanan per karyawan
		# 1. periksa apakah rekap grading bulanan sudah ada? gunakan method find_monthly_grading(month_id, year)
		monthly_grading_ids = self._find_monthly_grading(self.month_ids, self.tgl_dibuat)
		monthly_kpi_line_values = []
		sequence = 0
		for month in self.month_ids:
			sequence += 1
			monthly_kpi_line_values.append((Command.create({
			'sequence' : sequence,
			'name' : f'{month.name} {self.tgl_dibuat.strftime("%Y")}',
			'month_id' : month.id,
			'monthly_grading_id' : monthly_grading_ids.filtered(lambda m:m.month_id == month).id,
			'employee_kpi_batch_id' : self.id,
		})))
		
		
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
		ro_employee_kpi_ids, alw_employee_kpi_ids = self._create_employee_kpi()
		return self.write({'state' : 'in_progress'})
	
	def button_submit(self):
		# print(any(line.absen == 0 or line.more == 0 for line in self.employee_kpi_line))
		if any(line.absen == 0 or line.more == 0 for line in self.employee_kpi_line):
			raise ValidationError(_("Kolom Absen dan kolom More RO tidak boleh berisi 0"))
		if any(line.absen == 0 for line in self.employee_alw_kpi_line):
			raise ValidationError(_("Kolom Absen ALrandom.randint(0,200)W tidak boleh berisi 0"))
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
	
	def action_show_details_ro(self):
		self.ensure_one()
		tree_view = self.env.ref('mum_kpi.employee_kpi_view_tree')
		form_view = self.env.ref('mum_kpi.employee_kpi_view_form')
		return {
			'name': _('Detail KPI RO'),
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'employee.kpi',
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