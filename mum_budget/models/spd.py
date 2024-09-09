from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError


class SPD(models.Model):
	_name = 'mum.spd'
	_inherit = ['mail.activity.mixin', 'mail.thread']
	_description = 'Surat Perjalanan Dinas'

	name = fields.Char(string='Nomor')
	tgl_dokumen = fields.Date(string='Tanggal Dokumen')
	program_kerja_id = fields.Many2one(comodel_name='mum.program.kerja', string='Program Kerja')
	divisi_id = fields.Many2one(comodel_name='hr.department', string='Divisi', domain=[('divisi', '=', True)])
	pemberi_tugas_id = fields.Many2one(comodel_name='hr.employee', string='Pemberi Tugas')
	jabatan_pemberi_tugas_id = fields.Many2one(comodel_name='job.title', string='Jabatan/Pangkat')
	bagian_pemberi_tugas_id = fields.Many2one(comodel_name='hr.department', string='Bagian')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Penerima Tugas')
	employee_title_id = fields.Many2one(comodel_name='job.title', string='Jabatan/Pangkat')
	employee_department_id = fields.Many2one(comodel_name='hr.department', string='Bagian')
	description = fields.Text(string='Maksud Perjalanan Dinas')
	lokasi = fields.Char(string='Lokasi')
	date_from = fields.Date(string='Start Date')
	date_to =  fields.Date(string='End Date')
	karyawan_pengikut_ids = fields.Many2many(comodel_name='hr.employee', string='Pengikut')

	uang_saku_ids = fields.One2many(comodel_name='uang.saku.spd', inverse_name='spd_id', string='Uang Saku Perjalanan Dinas')
	total_biaya_uang_saku = fields.Monetary('Total Uang Saku')

	uang_penginapan_ids = fields.One2many(comodel_name='uang.penginapan.spd', inverse_name='spd_id', string='Uang Penginapan Perjalanan Dinas')
	total_biaya_penginapan = fields.Monetary('Total Penginapan')

	biaya_transportasi_lokal_ids = fields.One2many(comodel_name='biaya.transportasi.lokal.spd', inverse_name='spd_id', string='Biaya Transportasi Lokal')
	total_transport_lokal = fields.Monetary('Total Transportasi Lokal')

	biaya_transportasi_utama_ids = fields.One2many(comodel_name='biaya.transportasi.utama.spd', inverse_name='spd_id', string='Biaya Transportasi Utama')
	total_transportasi_utama = fields.Monetary('Total Transportasi Utama')

	biaya_penjamuan_ids = fields.One2many(comodel_name='biaya.penjamuan.spd', inverse_name='spd_id', string='Biaya Penjamuan')
	total_biaya_penjamuan = fields.Monetary('Total Biaya Penjamuan')

	biaya_lainnya_ids = fields.One2many(comodel_name='biaya.lain.spd', inverse_name='spd_id', string='Biaya Lainnya')
	total_biaya_lain = fields.Monetary('Total Biaya Lain-lain')

	currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', default=lambda s:s.env.company.currency_id.id)
	total_biaya = fields.Float(string='Total Biaya')

	state = fields.Selection([
		('draft', 'Draft'),
		('confirm', 'Confirmed'),
		('approval_1', 'Approval 1'),
		('approval_2', 'Approval 2'),
		('pelaporan', 'Pelaporan'),
		('done', 'Done'),
		('cancel', 'Cancel'),
	], string='Status', default='draft', copy=False, tracking=1)

	
	@api.constrains('karyawan_pengikut_ids')
	def _check_karyawan_pengikut_ids(self):
		# CODE HERE
		if len(self.karyawan_pengikut_ids) > 3:
			raise ValidationError(_("Pengikut maksimal 3 orang."))

	#CRUD METHOD
	@api.model
	def create(self,vals):
		employee_id = self.env['hr.employee'].browse(vals.get('employee_id'))
		name = self.env['ir.sequence'].next_by_code('spd.cabang.seq')
		if employee_id.cabang_id.pusat:
			name = self.env['ir.sequence'].next_by_code('spd.pusat.seq')
		vals['name'] = name
		return super().create(vals)

	def write(self,vals):
		return super().write(vals)

	def unlink(self):
		return super().unlink()



	#LOGIC METHOD
	@api.onchange('pemberi_tugas_id')
	def _onchange_pemberi_tugas_id(self):
		self.jabatan_pemberi_tugas_id = self.pemberi_tugas_id and self.pemberi_tugas_id.job_title_id.id or False
		self.bagian_pemberi_tugas_id = self.pemberi_tugas_id and self.pemberi_tugas_id.department_id.id or False

	@api.onchange('employee_id')
	def _onchange_employee_id(self):
		self.employee_title_id = self.employee_id and self.employee_id.job_title_id.id or False
		self.employee_department_id = self.employee_id and self.employee_id.department_id.id or False
		
	def _generate_biaya_values(self, employee_ids, params, item_biaya=False):
		values = []
		for employee in employee_ids:
			values.append(Command.create({
				'employee_id' : employee.id,
				'product_id' : params,
				'amount' : item_biaya and getattr(employee.job_title_id, item_biaya) or 0,
			}))

		return values

	

	def _prepare_biaya_values(self):
		params = self.env['ir.config_parameter'].sudo()
		employee_ids = self.employee_id + self.karyawan_pengikut_ids
		uang_saku_vals = self._generate_biaya_values(employee_ids, params.get_param('mum_budget.default_item_uang_saku_spd_id'), 'uang_saku_spd')
		uang_penginapan_vals = self._generate_biaya_values(employee_ids, params.get_param('mum_budget.default_item_penginapan_spd_id'), 'uang_penginapan_spd')
		biaya_transportasi_lokal_vals = self._generate_biaya_values(employee_ids, params.get_param('mum_budget.default_item_transportasi_lokal_spd_id'))
		biaya_transportasi_utama_vals = self._generate_biaya_values(employee_ids, params.get_param('mum_budget.default_item_trans_utama_berangkat_spd_id'))
		biaya_penjamuan_vals = self._generate_biaya_values(employee_ids, params.get_param('mum_budget.default_item_penjamuan_spd_id'))
		biaya_lainnya_vals = self._generate_biaya_values(employee_ids, params.get_param('mum_budget.default_item_lainnya_spd_id'))

		return {
			'uang_saku_ids' : uang_saku_vals,
			'uang_penginapan_ids' : uang_penginapan_vals,
			'biaya_transportasi_lokal_ids' : biaya_transportasi_lokal_vals,
			'biaya_transportasi_utama_ids' : biaya_transportasi_utama_vals,
			'biaya_penjamuan_ids' : biaya_penjamuan_vals,
			'biaya_lainnya_ids' : biaya_lainnya_vals,
		}
	


	#BUTTON METHOD
	def button_submit(self):
		submit_values = self._prepare_biaya_values()
		submit_values.update({'state' : 'confirm'})
		return self.write(submit_values)
	
	def button_confirm(self):
		return self.write({'state' : 'approval_1'})
	
	def button_approve_1(self):
		return self.write({'state' : 'approval_2'})
	
	def button_approve_2(self):
		return self.write({'state' : 'pelaporan'})
	
	# def button_approve_3(self):
	# 	return self.write({'state' : 'pelaporan'})
	
	def button_done(self):
		return self.write({'state' : 'done'})
	
	def button_cancel(self):
		return self.write({'state' : 'cancel'})



	#ACTION METHOD


class UangSakuSpd(models.Model):
	_name = 'uang.saku.spd'
	_description = 'Uang Saku SPD'
	_rec_name = 'employee_id'

	spd_id = fields.Many2one(comodel_name='mum.spd', string='SPD')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan')
	product_id = fields.Many2one(comodel_name='product.product', string='Item Biaya')
	jml_hari = fields.Integer(string='Waktu (Hari)')
	amount = fields.Float(string='Biaya/hari')
	total = fields.Float(string='Total', compute='_compute_total')

	#LOGIC METHOD
	@api.depends('jml_hari', 'amount')
	def _compute_total(self):
		for rec in self:
			rec.total = rec.jml_hari * rec.amount



	#BUTTON METHOD



	#ACTION METHOD

class UangPenginapanSpd(models.Model):
	_name = 'uang.penginapan.spd'
	_description = 'Uang Penginapan SPD'
	_rec_name = 'employee_id'

	spd_id = fields.Many2one(comodel_name='mum.spd', string='SPD')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan')
	product_id = fields.Many2one(comodel_name='product.product', string='Item Biaya')
	jml_hari = fields.Integer(string='Waktu (Hari)')
	amount = fields.Float(string='Biaya/hari')
	total = fields.Float(string='Total', compute='_compute_total')

	#LOGIC METHOD
	@api.depends('jml_hari', 'amount')
	def _compute_total(self):
		for rec in self:
			rec.total = rec.jml_hari * rec.amount



	#BUTTON METHOD



	#ACTION METHOD

class BiayaTransportasiLokalSpd(models.Model):
	_name = 'biaya.transportasi.lokal.spd'
	_description = 'Biaya Transportasi Lokal SPD'
	_rec_name = 'employee_id'

	spd_id = fields.Many2one(comodel_name='mum.spd', string='SPD')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan')
	product_id = fields.Many2one(comodel_name='product.product', string='Item Biaya')
	jml_hari = fields.Integer(string='Waktu (Hari)')
	amount = fields.Float(string='Biaya/hari')
	total = fields.Float(string='Total', compute='_compute_total')

	#LOGIC METHOD
	@api.depends('jml_hari', 'amount')
	def _compute_total(self):
		for rec in self:
			rec.total = rec.jml_hari * rec.amount



	#BUTTON METHOD



	#ACTION METHOD

class BiayaTransportasiUtamaSpd(models.Model):
	_name = 'biaya.transportasi.utama.spd'
	_description = 'Biaya Transportasi Utama'
	_rec_name = 'employee_id'

	spd_id = fields.Many2one(comodel_name='mum.spd', string='SPD')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan')
	product_id = fields.Many2one(comodel_name='product.product', string='Item Biaya')
	tiket_uang = fields.Selection([('tiket', 'Tiket'), ('uang', 'Uang')], default='tiket', string='Tiket/Uang')
	amount = fields.Float(string='Biaya Tiket')
	jenis_transportasi = fields.Selection([
		('pesawat', 'Pesawat'),
		('ka', 'Kereta Api'),
		('bus', 'Bus'),
		('lainnya', 'Lainnya'),
		], default='lainnya', string="Jenis Transportasi")
	airport_tax = fields.Float(string='Airport Tax')
	

	#LOGIC METHOD
	# def _compute_total(self):
	#     for rec in self:
	#         rec.total = rec.jml_hari * rec.amount



	#BUTTON METHOD



	#ACTION METHOD

class BiayaPenjamuanSpd(models.Model):
	_name = 'biaya.penjamuan.spd'
	_description = 'Biaya Penjamuan SPD'
	_rec_name = 'employee_id'

	def _get_default_product_id(self):
		return self.env['ir.config_parameter'].sudo().get_param('mum_budget.default_item_penjamuan_spd_id')


	spd_id = fields.Many2one(comodel_name='mum.spd', string='SPD')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan')
	product_id = fields.Many2one(comodel_name='product.product', string='Item Biaya', default=_get_default_product_id)
	amount = fields.Float(string='Biaya')

	#LOGIC METHOD
	# def _compute_total(self):
	#     for rec in self:
	#         rec.total = rec.jml_hari * rec.amount



	#BUTTON METHOD



	#ACTION METHOD

class BiayaLainnyaSpd(models.Model):
	_name = 'biaya.lain.spd'
	_description = 'Biaya Lainnya SPD'
	_rec_name = 'employee_id'

	def _get_default_product_id(self):
		return self.env['ir.config_parameter'].sudo().get_param('mum_budget.default_item_lainnya_spd_id')

	spd_id = fields.Many2one(comodel_name='mum.spd', string='SPD')
	product_id = fields.Many2one(comodel_name='product.product', string='Item Biaya', default=_get_default_product_id)
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan')
	amount = fields.Float(string='Biaya')


	#CRUD METHOD
	@api.model
	def create(self,vals):
		return super().create(vals)

	def write(self,vals):
		return super().write(vals)

	def unlink(self):
		return super().unlink()



	#LOGIC METHOD



	#BUTTON METHOD



	#ACTION METHOD
