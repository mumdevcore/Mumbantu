from odoo import _, api, fields, models


class ResMonth(models.Model):
	_name = 'res.month'
	_description = 'Res Month'

	sequence = fields.Char(string='Urutan')
	name = fields.Char(string='Nama Bulan')

class KpiPeriode(models.Model):
	_name = 'kpi.periode'
	_description = "KPI Periode"

	name = fields.Char(string='Nama Periode')
	month_ids = fields.Many2many(comodel_name='res.month', string='Bulan')

class WilayahSuffer(models.Model):
	_name = 'wilayah.suffer'
	_description = 'Wilayah Suffer'

	name = fields.Char(string='Wilayah Suffer')
	nilai_insentif = fields.Float(string='Nilai Insentif')