# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, Command, _

class HrTraining(models.Model):
	_name = 'hr.training'
	_description = 'HR Training Model'
	_check_company_auto = True
	
	name = fields.Char(string='Tema Training',)
	company_id = fields.Many2one('res.company',string='Company', default=lambda self:self.env.company)

class EksternalGroup(models.Model):
	_name = 'eksternal.group'
	_description = 'Eksternal Group Mitra Bisnis'
	_check_company_auto = True

	name = fields.Char(string='Name',)
	company_id = fields.Many2one('res.company',string='Company', default=lambda self:self.env.company)

class res_agama(models.Model):
	_name = 'res.agama'
	_description = 'Agama'

	name = fields.Char(string='Agama',)

class status_pajak(models.Model):
	_name = 'status.pajak'
	_description = 'Status Pajak'

	name = fields.Char(string='Status Pajak',)

class ResCabang(models.Model):
	_name = 'res.cabang'
	_description = 'Res Cabang'

	name = fields.Char(string='Nama Cabang',)
	kota_id = fields.Many2one('vit.kota',string='Kota',)
	# company_id = fields.Many2one('source.model.name',string='Field Label',)

class JobTitle(models.Model):
	_name = 'job.title'
	_description = 'Job Title'

	name = fields.Char(string='Job Title',)
	
class ResMonth(models.Model):
	_name = 'res.month'
	_description = 'Res Month'

	sequence = fields.Char(string='Urutan')
	name = fields.Char(string='Nama Bulan')

class InsentifPeriode(models.Model):
	_name = 'insentif.periode'
	_description = "Periode Insentif"

	name = fields.Char(string='Nama Periode')
	month_ids = fields.Many2many(comodel_name='res.month', string='Bulan')