from odoo import _, api, fields, models, Command


class HrDepartment(models.Model):
	_inherit = 'hr.department'
	_rec_name = 'name'

	@api.depends('name', 'parent_id.name')
	def _compute_complete_name(self):
		for department in self:
			if department.parent_id:
				department.complete_name = '%s / %s' % (department.parent_id.name, department.name)
			else:
				department.complete_name = department.name

	def name_get(self):
		name = []
		for rec in self:
			name_get = rec.name
			if rec.parent_id:
				name_get = f"{rec.parent_id.name} / {rec.name}"
			name.append((rec.id, name_get))
		return name