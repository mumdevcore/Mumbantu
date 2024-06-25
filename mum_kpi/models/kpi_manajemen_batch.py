from odoo import _, api, fields, models, Command

class KpiManajemenBatch(models.Model):
	_name = 'kpi.manajemen.batch'
	_description = 'KPI Manajemen Batch'

	# Semua objek yang berhubungan dengan KPI Manajemen harus memiliki foreign key kpi.manajemen.batch, dan diberi nama field kpi_manajemen_batch_id
	name = fields.Char(string='Nomor')
	periode_id = fields.Many2one(comodel_name='kpi.periode', string='Periode')
	month_ids = fields.Many2many(comodel_name='res.month', string='Month')
	tahun = fields.Char(string='Tahun')
	employee_manajemen_kpi_ids = fields.One2many(comodel_name='employee.manajemen.kpi', inverse_name='kpi_manajemen_batch_id', string='KPI Manajemen')

	def _find_manajemen_batch(self, periode_id, tahun, tgl_dibuat):
		manajemen_batch_id = self.sudo().search([('periode_id', '=', periode_id.id), ('tahun', '=', tahun)])
		if not manajemen_batch_id:
			manajemen_batch_id = self.sudo().create({'name' : f"{periode_id.name}-{tahun}",'periode_id' : periode_id.id, 'tahun' : tahun})
		
		return manajemen_batch_id