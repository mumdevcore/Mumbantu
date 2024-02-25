# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, Command, _

class HrJobPosition(models.Model):
	_inherit = 'hr.job'

	inisial = fields.Char(string='Inisial Jabatan',)