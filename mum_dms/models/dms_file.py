from odoo import _, api, fields, models, Command


class DmsFile(models.Model):
	_name = 'dms.file'
	_inherit = ['dms.file', 'base.revision']

	masa_berlaku_awal = fields.Date(string='Masa Berlaku Awal')
	masa_berlaku_akhir = fields.Date(string='Masa Berlaku Akhir')
	attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Attachments')
	current_revision_id = fields.Many2one(
		comodel_name="dms.file",
	)
	old_revision_ids = fields.One2many(
		comodel_name="dms.file",
	)

	def _get_new_rev_data(self, new_rev_number):
		self.ensure_one()
		res = super()._get_new_rev_data(new_rev_number)
		return {
			"revision_number": new_rev_number,
			"unrevisioned_name": self.unrevisioned_name,
			"name": self.name,
			"old_revision_ids": [(4, self.id, False)],
		}

	def _prepare_revision_data(self, new_revision):
		vals = super()._prepare_revision_data(new_revision)
		# vals.update({"state": "cancel"})
		return vals

	def action_view_revisions(self):
		self.ensure_one()
		action = self.env.ref("izm_backend_custom.action_sale_forecast")
		result = action.read()[0]
		result["domain"] = ["|", ("active", "=", False), ("active", "=", True)]
		result["context"] = {
			"active_test": 0,
			"search_default_current_revision_id": self.id,
			"default_current_revision_id": self.id,
		}
		return result