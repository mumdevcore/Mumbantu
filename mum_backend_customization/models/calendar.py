# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, Command, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class HrCalendarCertification(models.Model):
	# _name = 'hr.calendar.certification'
	_inherit = 'calendar.event'

	name = fields.Char(default='/', copy=False)
	tipe_calendar = fields.Selection([
		('training_manajemen', 'Training Manajemen'),
		('training_eksternal', 'Training Eksternal'),
		('meeting', 'Meeting')], string="Tipe Jadwal", copy=False, tracking=True, default='meeting')
	employee_ids = fields.Many2many('hr.employee',string='Employees',)
	eksternal_group_ids = fields.Many2many('eksternal.group',string='Eksternal Groups',)
	hr_certification_line = fields.One2many('hr.certification','calendar_id',string='Certification Details',)
	hr_certification_count = fields.Integer(string='HR Certification Count', compute='_compute_hr_certification_count')
	user_id = fields.Many2one(string='Dibuat oleh',)

	tipe_kegiatan = fields.Selection([
		('training', "Training"),
		('sertifikasi', 'Sertifikasi'),
		], string="Jenis Kegiatan", default='training', copy=False, tracking=True)
	kualifikasi_training = fields.Selection([
		('manajemen', "Manajemen"),
		('eksternal', 'Eksternal'),
		], string="Kualifikasi Training", default='manajemen', copy=False, tracking=True)
	hr_training_id = fields.Many2one('hr.training',string='Nama Kegiatan', tracking=True)
	total_days = fields.Integer(string='Jumlah Hari', tracking=True, compute='_compute_total_days')
	total_hours = fields.Float(string='Jumlah Jam Kegiatan', tracking=True)
	total_attendees = fields.Integer(string='Total Peserta', tracking=True)
	location = fields.Char(string='Lokasi Pelaksanaan',)
	trainer_partner_ids = fields.Many2many('res.partner', "calendar_trainer_partner_rel",string='Trainer', tracking=True)
	currency_id = fields.Many2one('res.currency',string='Currency', default=lambda s:s.env.company.currency_id)
	budget_plan = fields.Monetary(string='RAB', tracking=True, currency_field='currency_id')
	budget_realisation = fields.Monetary(string='Realisasi Anggaran', tracking=True, currency_field='currency_id')
	notes = fields.Text(string='Keterangan',)
	state = fields.Selection([
		('draft', 'Draft'),
		('confirm', 'On Progress'),
		('done', 'Done'),
		('cancel', 'Cancel'),], string='State', default='draft')

	@api.model
	def create(self, vals):
		if vals.get('tipe_calendar') in ('training_manajemen', 'training_eksternal'):
			vals['name'] = self.env['ir.sequence'].next_by_code('event.calendar.seq', fields.Date.to_date(vals.get('start_date')))
		return super(HrCalendarCertification, self).create(vals)

	def _compute_hr_certification_count(self):
		for rec in self:
			rec.hr_certification_count = len(rec.hr_certification_line)

	def _compute_total_days(self):
		for rec in self:
			rec.total_days = 0
			if rec.start_date and rec.stop_date:
				total_days = rec.stop_date - rec.start_date + timedelta(days=1)
				rec.total_days = total_days.days


	def action_view_hr_certification(self):
		xml_id = self.kualifikasi_training == 'manajemen' and 'mum_backend_customization.action_hr_certification_manajemen' or 'mum_backend_customization.action_hr_certification_eksternal'
		action = self.env["ir.actions.actions"]._for_xml_id(xml_id)
		if len(self.hr_certification_line) > 1:
			action['domain'] = [('id', 'in', self.hr_certification_line.ids)]
		elif len(self.hr_certification_line) == 1:
			action['views'] = [(self.env.ref('mum_backend_customization.hr_certification_view_form').id, 'form')]
			action['res_id'] = self.hr_certification_line.ids[0]
		else:
			action = {'type': 'ir.actions.act_window_close'}
		return action

	def _prepare_certification_values(self, employee_id=False, eksternal_group_id=False):
		return {
			'start_date' : self.start_date,
			'end_date' : self.stop_date,
			'calendar_id' : self.id,
			'employee_id' : employee_id,
			'eksternal_group_id' : eksternal_group_id,
			'tipe_kegiatan' : self.tipe_kegiatan,
			'kualifikasi_training' : self.kualifikasi_training,
			'hr_training_id' : self.hr_training_id.id,
			# 'total_days' : self.total_days,
			'total_attendees' : self.total_attendees,
			'location' : self.location,
			'trainer_partner_ids' : self.trainer_partner_ids, 
			'budget_plan' : self.budget_plan,
			'budget_realisation' : self.budget_realisation,
			'notes' : self.notes,
			'user_id' : self.user_id.id,
		}

	def button_confirm(self):
		if self._context.get('force_submit') or self.kualifikasi_training == 'eksternal':
			self.hr_certification_line.write({'state' : 'in_progress'})
			return self.write({'state' : 'confirm'})

		employee_in_tna = self.env['training.needs.analysis'].search([('hr_training_id', '=', self.hr_training_id.id), ('state', '=', 'submit')]).employee_id
		# existing_employees = self.hr_certification_line.employee_id
		suggestion_employee_ids = employee_in_tna.filtered(lambda s:s.id not in self.hr_certification_line.employee_id.ids)

		if suggestion_employee_ids:
			view = self.env.ref('mum_backend_customization.training_employee_suggestion_wizard_view_form')
			return {
				'name': _('Tambah Peserta?'),
				'type': 'ir.actions.act_window',
				'view_mode': 'form',
				'res_model': 'training.employee.suggestion.wizard',
				'views': [(view.id, 'form')],
				'view_id': view.id,
				'target': 'new',
				'context': dict(self.env.context, default_calendar_id=self.id, default_employee_ids=[Command.set(suggestion_employee_ids.ids)]),
			}

		self.hr_certification_line.write({'state' : 'in_progress'})
		return self.write({'state' : 'confirm'})
		

	def button_done(self):
		if any(x.dokumentasi == False for x in self.hr_certification_line):
			raise ValidationError(_("Wajib melampirkan dokumen."))

		if self.kualifikasi_training == 'eksternal':
			self.hr_certification_line.write({'state':'done'})
		return self.write({'state' : 'done'})

	def button_cancel(self):
		return self.write({'state' : 'cancel'})

	def button_draft(self):
		return self.write({'state' : 'draft'})