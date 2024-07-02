from odoo import _, api, fields, models


# class ResMonth(models.Model):
# 	_name = 'res.month'
# 	_description = 'Res Month'

# 	sequence = fields.Char(string='Urutan')
# 	name = fields.Char(string='Nama Bulan')


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


class ServiceQuality(models.Model):
	_name = 'kpi.service.quality'
	_description = 'Service Quality'

	name = fields.Char(string='Code')
	nilai = fields.Float(string='Nilai')

class ManajemenAbsensi(models.Model):
	_name = 'kpi.manajemen.absensi'
	_description = 'Manajemen Absensi'

	name = fields.Char(string='Code')
	nilai = fields.Float(string='Nilai')

class KpiManajemenGrading(models.Model):
	_name = 'kpi.manajemen.grade'
	_description = 'KPI Manajemen Grade'

	name = fields.Char(string='Grade')
	nilai = fields.Float(string='Nilai')
	job_title_id = fields.Many2one(comodel_name='job.title', string='Title')


class JobTitle(models.Model):
	_inherit = 'job.title'

	manajemen_grade_ids = fields.One2many(comodel_name='kpi.manajemen.grade', inverse_name='job_title_id', string='KPI Manajemen Grade')