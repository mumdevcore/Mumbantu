from odoo import _, api, fields, models, Command


class DmsFile(models.Model):
	_inherit = 'dms.file'
	# _inherit = ['dms.file', 'base.revision']

	masa_berlaku_awal = fields.Date(string='Masa Berlaku Awal')
	masa_berlaku_akhir = fields.Date(string='Masa Berlaku Akhir')
	attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Attachments')
	revisi = fields.Integer(string='Pembaharuan', compute='_compute_revisi')
	user_allowed_ids = fields.Many2many(comodel_name='res.users', string='User Allowed', compute='_compute_user_allowed_ids')

	def _compute_user_allowed_ids(self):
		for rec in self:
			rec.user_allowed_ids = rec.directory_id.group_ids.users

	def _compute_revisi(self):
		for rec in self:
			rec.revisi = len(rec.attachment_ids)