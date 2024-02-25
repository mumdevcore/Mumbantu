# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, Command, _

class TrainingEmployeeSuggestionWizard(models.TransientModel):
	_name = 'training.employee.suggestion.wizard'
	_description = "Training Employee Suggestion Wizard"

	calendar_id = fields.Many2one('calendar.event',string='Calendar',)
	employee_ids = fields.Many2many('hr.employee',string='Employees',)

	# @api.model
	# def default_get(self, fields):
	# 	default = super().default_get(fields)

	# 	return default

	def submit_employee(self):
		cert_values = [Command.create(self.calendar_id._prepare_certification_values(employee_id=employee.id)) for employee in self.employee_ids]
		self.calendar_id.write({'hr_certification_line' : cert_values})
		self.calendar_id.with_context(force_submit=True).button_confirm()

	def skip_employee(self):
		self.calendar_id.with_context(force_submit=True).button_confirm()




