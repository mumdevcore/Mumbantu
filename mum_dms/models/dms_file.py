from odoo import _, api, fields, models, Command


class DmsFile(models.Model):
	_inherit = 'dms.file'
	# _inherit = ['dms.file', 'base.revision']

	masa_berlaku_awal = fields.Date(string='Masa Berlaku Awal')
	masa_berlaku_akhir = fields.Date(string='Masa Berlaku Akhir')
	attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Attachments')
	revisi = fields.Integer(string='Revisi', default=0)

	def create_revision(self):
		self.revisi += 1
		print('create_revision')