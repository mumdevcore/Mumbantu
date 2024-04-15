from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError


class GradingMasterTemplate(models.Model):
	_name = 'grading.template'
	_description = 'Grading Master Template'
	_rec_name = 'grade'

	# Nilai ditulis dalam persen, pastikan memberikan widget percentage pada xml
	
	# Template utk semua.
	grade = fields.Char(string='Grade')
	nilai_min_absen = fields.Integer(string='Nilai Min Absensi', default=0)
	nilai_max_absen = fields.Integer(string='Nilai Max Absensi', default=0)
	potongan_absen = fields.Float(string='Pengurangan Absensi', default=0)

	# Template RO
	nilai_min_more = fields.Integer(string='Nilai Min MORE', default=0)
	nilai_max_more = fields.Integer(string='Nilai Max MORE', default=0)
	nilai_min = fields.Float(string='Nilai Min', default=0)
	nilai_max = fields.Float(string='Nilai Max', default=0)
	nilai_min_ro = fields.Float(string='Min RO', default=0)
	nilai_max_ro = fields.Float(string='Max RO', default=0)
	insentif_more = fields.Float(string='Insentif MORE', default=0)
	insentif_rekrutmen = fields.Float(string='Insentif Rekrutmen', default=0)
	insentif_maintain = fields.Float(string='Insentif Maintain', default=0)
	insentif_tl = fields.Float(string='Insentif TL', default=0)
	wilayah_suffer_id  = fields.Many2one(comodel_name='wilayah.suffer', string='Wilayah Suffer')

	# Template ALW
	nilai_min_alw_resign = fields.Float(string='Min ALW Resign', default=0)
	nilai_max_alw_resign = fields.Float(string='Max ALW Resign', default=0)
	nilai_min_alw_incomplete_data = fields.Float(string='Min ALW Incomplete Data', default=0)
	nilai_max_alw_incomplete_data = fields.Float(string='Max ALW Incomplete Data', default=0)
	nilai_min_alw_pkwt = fields.Float(string='Min ALW PKWT', default=0)
	nilai_max_alw_pkwt = fields.Float(string='Max ALW PKWT', default=0)
	nilai_min_alw_ppkwt = fields.Float(string='Min ALW PPKWT', default=0)
	nilai_max_alw_ppkwt = fields.Float(string='Max ALW PPKWT', default=0)
	insentif_alw_resign = fields.Float(string='Insentif ALW Resign', default=0)
	insentif_alw_incomplete_data = fields.Float(string='Insentif ALW Incomplete Data', default=0)
	insentif_alw_pkwt = fields.Float(string='Insentif ALW PKWT', default=0)
	insentif_alw_ppkwt = fields.Float(string='Insentif ALW PPKWT', default=0)

	# Template KRO
	nilai_min_alw_avg = fields.Float(string='Min ALW Average', default=0)
	nilai_max_alw_avg = fields.Float(string='Max ALW Average', default=0)
	nilai_min_ro_avg = fields.Float(string='Min KRO', default=0)
	nilai_max_ro_avg = fields.Float(string='Max KRO', default=0)
	insentif_kro_ro = fields.Float(string='Insentif KRO RO', default=0)
	insentif_kro_alw = fields.Float(string='Insentif KRO ALW', default=0)

	# Template Portofolio
	nilai_min_portofolio_kekurangan = fields.Integer(string='Nilai Min Kekurangan', default=0)
	nilai_max_portofolio_kekurangan = fields.Integer(string='Nilai Max Kekurangan', default=0)
	nilai_min_portofolio_incomplete_data = fields.Float(string='Nilai Min Incomplete', default=0)
	nilai_max_portofolio_incomplete_data = fields.Float(string='Nilai Max Incomplete', default=0)
	nilai_min_portofolio_sla = fields.Integer(string='Nilai Min SLA', default=0)
	nilai_max_portofolio_sla = fields.Integer(string='Nilai Max SLA', default=0)
	insentif_portofolio_kekurangan = fields.Float(string='Insentif Kekurangan ')
	insentif_portofolio_incomplete_data = fields.Float(string='Insentif Incomplete Data')
	insentif_portofolio_sla = fields.Float(string='Insentif SLA')



	


class GradingMaster(models.Model):
	_name = 'monthly.grading'
	_description = 'Grading Bulanan'

	name = fields.Char(string='Name')
	periode_id = fields.Many2one(comodel_name='kpi.periode', string='Periode')
	month_id = fields.Many2one(comodel_name='res.month', string='Month')
	kpi_mekaar_batch_id = fields.Many2one(comodel_name='kpi.mekaar.batch', string='KPI Mekaar Batch')
	tahun = fields.Char(string='Tahun')
	employee_monthly_kpi_line = fields.One2many(comodel_name='employee.monthly.kpi.line', inverse_name='monthly_grading_id', string='Insentif RO Line')
	alw_monthly_kpi_line = fields.One2many(comodel_name='alw.monthly.kpi.line', inverse_name='monthly_grading_id', string='Insentif ALW Line')
	# employee_kpi_grading_ids = fields.One2many(comodel_name='employee.kpi.grading', inverse_name='monthly_grading_id', string='Employee KPI Grading', ondelete='cascade')
	resume_kpi_grading_ids = fields.One2many(comodel_name='resume.kpi.grading', inverse_name='monthly_grading_id', string='Resume KPI Grading', ondelete='cascade')

	@api.model
	def create(self, values):
		month_id = self.env['res.month'].browse(values.get('month_id'))
		if not month_id or not values.get('tahun'):
			raise ValidationError(_("Bulan dan Tahun harus diisi."))
		values['name'] = f"{month_id.name}-{values.get('tahun')}"
		return super(GradingMaster, self).create(values)
	
	def _create_employee_kpi_grading(self, employee_monthly_kpi_line_ids):
		employee_kpi_grading_ids = self.env['employee.kpi.grading']

		for grading in self:
			filtered_employee_kpi_line_ids = employee_monthly_kpi_line_ids.filtered(lambda l:l.month_id == grading.month_id)
			employee_kpi_grading_vals = [{
				'monthly_grading_id' : grading.id,
				'employee_id' : employee_kpi_line_id.employee_id.id,
				'employee_monthly_kpi_line_id' : employee_kpi_line_id.id,
			} for employee_kpi_line_id in filtered_employee_kpi_line_ids]
			employee_kpi_grading_ids.create(employee_kpi_grading_vals)
		
		return employee_kpi_grading_ids
	
	def _find_monthly_grading(self, monthly_ids, periode_id, tgl_dibuat):
		monthly_grading_ids = self.env['monthly.grading'].search([('month_id', 'in', monthly_ids.ids), ('tahun', '=', tgl_dibuat.strftime('%Y'))])
		# cek apakah ada grading bulanan yang belum terbentuk, jika ada maka buat grading bulanan dan masukkan ke dalam monthly_grading_ids
		# sintaks symmetric_difference adalah built-in function tipe data set, yg berfungsi utk mencari perbedaan dari 2 dataset
		monthly_grading_to_create = list(set(monthly_ids.ids).symmetric_difference(set(monthly_grading_ids.month_id.ids)))
		if monthly_grading_to_create:
			grading_template_values = [(Command.create({
				'grade_template_id' : template.id,
				# 'kpi_mekaar_batch_id' : self.kpi_mekaar_batch_id.id,
				'grade' : template.grade,
			})) for template in self.env['grading.template'].search([])]
			values = [{
				'periode_id' : periode_id.id,
				'month_id' : monthly_grading,
				'tahun' : tgl_dibuat.strftime("%Y"),
				'resume_kpi_grading_ids' : grading_template_values,
			} for monthly_grading in monthly_grading_to_create]
			created_monthly_grading_ids = self.env['monthly.grading'].create(values)
			# pertanyaan, apakah tanda |= pada odoo dapat diartikan menambahkan recordset yg baru ke recordset yg sudah ada ? BENARR
			monthly_grading_ids |= created_monthly_grading_ids
			
		return monthly_grading_ids
			
	
class ResumeKpiGrading(models.Model):
	_name = 'resume.kpi.grading'
	_description = 'Resume KPI Grading'
	_order = 'grade asc'
	_rec_name = 'grade_template_id'

	monthly_grading_id = fields.Many2one(comodel_name='monthly.grading', string='Monthly Grading', ondelete='cascade')
	kpi_mekaar_batch_id = fields.Many2one(comodel_name='kpi.mekaar.batch', string='KPI Mekaar Batch')
	grade_template_id = fields.Many2one(comodel_name='grading.template', string='Grading Template')
	grade = fields.Char(string='Grade')
	
	jumlah_ro = fields.Integer(string='Jumlah RO', compute='_compute_jumlah_ro_alw')
	jumlah_alw = fields.Integer(string='Jumlah ALW', compute='_compute_jumlah_ro_alw')
	
	# @api.depends('grade_template_id', 'monthly_grading_id')
	def _compute_jumlah_ro_alw(self):
		for rec in self:
			# kpi_monthly_ids = rec.monthly_grading_id.
			rec.jumlah_ro = 0
			rec.jumlah_alw = 0

	