# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, Command, _

class HrTraining(models.Model):
	_name = 'hr.training'
	_description = 'HR Training Model'
	_check_company_auto = True

	name = fields.Char(string='Tema Training',)
	company_id = fields.Many2one('res.company',string='Company', default=lambda self:self.env.company)