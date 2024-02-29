# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, Command, _

class ResCabang(models.Model):
	_name = 'res.cabang'
	_description = 'Res Cabang'

	name = fields.Char(string='Nama Cabang',)
	kota_id = fields.Many2one('vit.kota',string='Kota',)
	# company_id = fields.Many2one('source.model.name',string='Field Label',)