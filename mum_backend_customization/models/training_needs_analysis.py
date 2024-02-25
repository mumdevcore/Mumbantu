# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, Command, _

class TrainingNeedsAnalysis(models.Model):
	_name = 'training.needs.analysis'
	_inherit = ['mail.activity.mixin', 'mail.thread']
	_description = 'Training Needs Analysis'

	name = fields.Char(string='Name',)
	employee_id = fields.Many2one('hr.employee',string='Nama Karyawan',)
	tgl_diajukan = fields.Date(string='Tanggal Diajukan')
	job_id = fields.Many2one('hr.job',string='Posisi', related='employee_id.job_id')
	hr_certification_ids = fields.One2many('hr.certification', 'tna_id',string='Certification',)
	hr_training_id = fields.Many2one('hr.training',string='Nama Kegiatan',)
	state = fields.Selection([
		('draft', 'Draft'),
		('submit', 'Diajukan'),
		('done', 'Done'),
		('cancel', 'Cancel'),], string="State", default='draft', copy=False, tracking=True)

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('training.needs.analysis.seq')

		return super().create(vals)

	def button_submit(self):
		return self.write({'state' : 'submit'})