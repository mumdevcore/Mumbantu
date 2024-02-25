# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, Command, _

class calendar_add_member_wizard(models.TransientModel):
	_name = 'calendar.add.member.wizard'
	_description = "Calendar Add Member Wizard"

	calendar_id = fields.Many2one('calendar.event',string='Calendar',)
	tipe_calendar = fields.Selection(string='Tipe Kalendar', related='calendar_id.tipe_calendar')
	employee_ids = fields.Many2many('hr.employee',string='Employees',)
	eksternal_group_ids = fields.Many2many('eksternal.group',string='Eksternal Groups',)

	def button_add_member(self):
		if self.tipe_calendar == 'training_manajemen':
			self._add_member_karyawan()
		elif self.tipe_calendar == 'training_eksternal':
			self._add_member_eksternal_group()


	def _add_member_karyawan(self):
		existing_employee_ids = self.calendar_id.hr_certification_line.employee_id
		filtered_employees = self.employee_ids.filtered(lambda s:s.id not in existing_employee_ids.ids)
		cert_values = [Command.create(self.calendar_id._prepare_certification_values(employee_id=employee.id)) for employee in filtered_employees]
		self.calendar_id.write({'hr_certification_line' : cert_values})

	def _add_member_eksternal_group(self):
		eksternal_group_ids = self.calendar_id.hr_certification_line.eksternal_group_id
		filtered_groups = self.eksternal_group_ids.filtered(lambda s:s.id not in eksternal_group_ids.ids)
		cert_values = [Command.create(self.calendar_id._prepare_certification_values(eksternal_group_id=eksternal_group_id.id)) for eksternal_group_id in filtered_groups]
		self.calendar_id.write({'hr_certification_line' : cert_values})