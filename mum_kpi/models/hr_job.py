from odoo import _, api, fields, models, Command


class HrJob(models.Model):
	_inherit = 'hr.job'

	kpi_template_manajemen_ids = fields.One2many(comodel_name='kpi.template.manajemen', inverse_name='job_id', string='KPI Template')
	total_bobot = fields.Float(string='Total Bobot')
	
	def _prepare_ski_values(self, employee):
		values = []
		for template in self.kpi_template_manajemen_ids:
			values.append((Command.create({
				'job_id' : template.job_id.id,
				'ski' : template.ski,
				'kpi' : template.kpi,
				'bobot' : template.bobot,
				'target' : template.target,
			})))
		return values
		
	
