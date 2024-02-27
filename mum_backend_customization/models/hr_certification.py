# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, Command, _
from datetime import timedelta
from odoo.exceptions import ValidationError

class HrCertification(models.Model):
	_name = 'hr.certification'
	_inherit = ['mail.activity.mixin', 'mail.thread']
	_description = 'HR Employee Certification'
	_check_company_auto = True

	name = fields.Char(string='Nomor Transaksi',)
	calendar_id = fields.Many2one('calendar.event',string='Schedule')
	tna_id = fields.Many2one('training.needs.analysis',string='TNA ',)
	employee_id = fields.Many2one('hr.employee',string='Nama Karyawan', tracking=True, )
	eksternal_group_id = fields.Many2one('eksternal.group',string='Eksternal Group',)
	tipe_kegiatan = fields.Selection([
		('training', "Training"),
		('sertifikasi', 'Sertifikasi'),
		], string="Jenis Kegiatan", default='training', copy=False, tracking=True)
	kualifikasi_training = fields.Selection([
		('manajemen', "Manajemen"),
		('eksternal', 'Eksternal'),
		], string="Kualifikasi Training", default='training', copy=False, tracking=True)
	hr_training_id = fields.Many2one('hr.training',string='Nama Kegiatan', tracking=True)
	start_date = fields.Date(string='Tanggal Mulai', tracking=True)
	end_date = fields.Date(string='Tanggal Selesai', tracking=True)
	total_days = fields.Integer(string='Jumlah Hari', tracking=True, compute='_compute_total_days')
	total_hours = fields.Float(string='Jumlah Jam Kegiatan', tracking=True)
	total_attendees = fields.Integer(string='Total Peserta', tracking=True)
	location = fields.Char(string='Lokasi Pelaksanaan',)
	trainer_partner_ids = fields.Many2many('res.partner', string='Trainer', tracking=True)
	instansi_ids = fields.Many2many('res.partner', 'hr_certification_instansi_partner_rel',string='Instansi',)
	budget_plan = fields.Float(string='RAB', tracking=True)
	budget_realisation = fields.Float(string='Realisasi Anggaran', tracking=True)
	notes = fields.Text(string='Keterangan',)
	user_id = fields.Many2one('res.users', string='Penanggung Jawab', default=lambda self:self.env.user)
	masa_berlaku_sertifikat = fields.Integer(string='Masa Berlaku Sertifikat',)
	state = fields.Selection([
		('draft', 'Draft'),
		('in_progress', 'Training'),
		('done', 'Done'),
		('cancel', 'Cancel'),
		], string='State', copy=False, tracking=True, default='draft')
	status_sertifikasi = fields.Selection([
		('draft', 'Draft'),
		('lulus', 'Lulus'),
		('tidak_lulus', 'Tidak Lulus'),
		('cancel', 'Cancel'),
		], string='Status Sertifikas', copy=False, tracking=True, default='draft')
	
	company_id = fields.Many2one('res.company',string='Company', default=lambda self:self.env.company)
	document_ids = fields.One2many('certification.document.line','hr_certification_id',string='Dokumen Lampiran',)
	sertifikat = fields.Binary('Sertifikat',attachment=True,)

	@api.model
	def create(self, vals):
		sequence_code = vals.get('kualifikasi_training') == 'manajemen' and 'hr.certification.manajemen.seq' or 'hr.certification.eksternal.seq'
		vals['name'] = self.env['ir.sequence'].next_by_code(sequence_code)
		return super().create(vals)

	# def unlink(self):
	# 	for rec in self:
	# 		if rec.state == 'done':
	# 			raise ValidationError(_("Transaksi tidak dapat dihapus"))

	def _compute_total_days(self):
		for rec in self:
			rec.total_days = 0
			if rec.start_date and rec.end_date:
				total_days = rec.end_date - rec.start_date + timedelta(days=1)
				rec.total_days = total_days.days

	def button_lulus(self):
		if not self.sertifikat and self.tipe_kegiatan == 'sertifikasi':
			raise ValidationError(_("Sertifikat belum dilampirkan."))
			
		return self.write({'status_sertifikasi' : 'lulus', 'state' : 'done'})
	

	def button_tidak_lulus(self):
		return self.write({'status_sertifikasi' : 'tidak_lulus', 'state' : 'done'})

	def button_cancel(self):
		return self.write({'state' : 'cancel', 'status_sertifikasi' : 'cancel'})


class HrExternalCertification(models.Model):
	_name = 'hr.external.certification'
	# _inherit = 'hr.certification'
	_description = 'HR External Certification'
	_check_company_auto = True

	name = fields.Char(string='Nomor',)
	calendar_id = fields.Many2one('calendar.event',string='Schedule', domain=[('tipe_kegiatan', '=', 'training_eksternal')])
	# employee_id = fields.Many2one('hr.employee',string='Nama Karyawan', tracking=True)
	tipe_kegiatan = fields.Selection([
		('training', "Training"),
		('sertifikasi', 'Sertifikasi'),
		], string="Tipe Kegiatan", default='training', copy=False, tracking=True)
	hr_training_id = fields.Many2one('hr.training',string='Tema Pelatihan', tracking=True)
	start_date = fields.Date(string='Tanggal Mulai', tracking=True)
	end_date = fields.Date(string='Tanggal Selesai', tracking=True)
	total_days = fields.Integer(string='Jumlah Hari', tracking=True)
	total_hours = fields.Float(string='Jumlah Jam Pembelajaran', tracking=True)
	total_attendees = fields.Integer(string='Total Peserta', tracking=True)
	location = fields.Char(string='Lokasi Pelaksanaan',)
	partner_id = fields.Many2one('res.partner',string='Trainer', tracking=True)
	budget_plan = fields.Float(string='RAB', tracking=True)
	budget_realisation = fields.Float(string='Realisasi Anggaran', tracking=True)
	notes = fields.Text(string='Keterangan',)

	state = fields.Selection([
		('draft', 'Draft'),
		('done', 'Done'),
		('cancel', 'Cancel')], string='State', default='draft', tracking=True, copy=False)
	
	company_id = fields.Many2one('res.company',string='Company', default=lambda self:self.env.company)
	# document_ids = fields.One2many('certification.document.line','hr_external_certification_id',string='Dokumen Lampiran',)

class CertificationDocumentLine(models.Model):
	_name = 'certification.document.line'
	_description = 'Certification Document Line'
	_check_company_auto = True

	# hr_external_certification_id = fields.Many2one('hr.external.certification',string='HR External Certification',)
	hr_certification_id = fields.Many2one('hr.certification',string='HR Employee Certification',)
	name = fields.Char(string='Nama File',)
	document = fields.Binary(string='File',attachment=True,)
	company_id = fields.Many2one('res.company',string='Company', default=lambda self:self.env.company)



