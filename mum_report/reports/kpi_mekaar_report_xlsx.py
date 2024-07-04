from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError

class KpiMekaarRekapXlsx(models.AbstractModel):
	_name = 'report.mum_report.kpi_mekaar_report_xlsx'
	_inherit = 'report.report_xlsx.abstract'
	_description = 'Report Rekapitulasi Mekaar'
# Nama Karyawan	 Keterlambatan (Menit)	 MORE	Jumlah Kelolaan Unit Mekaar	 Formasi	 Aktif	 Rekrutmen	TL	 Kurang	 Grade Absensi	 Potongan Absensi	 Grade MORE	 Insentif MORE	 Pencapaian Rekrutment	Grade Rekrutmen	 Pencapaian Maintain	 Grade maintain	 Pencapaian TL	 Grade TL	 Insentif Aktif	 Insentif Rekrutmen	 Insentif TL	 Insenti Wilayah Suffer	Sum	Insentif Total	 Maintain

	def _get_header_ro(self):
		return [
			('name', 'Nama Karyawan'),
			('absensi', 'Keterlambatan'),
			('more', 'MORE'),
			('cabang', 'Jml Kelolaan'),
			('formasi', 'Formasi'),
			('aktif', 'Aktif'),
			('rekrutmen', 'Rekrutmen'),
			('tl', 'TL'),
			('kurang', 'Kurang'),
			('grade_absen_id', 'Grade Absensi'),
			('potongan_absen', 'Potongan Absensi'),
			('grade_more_id', 'Grade MORE'),
			('insentif_more', 'Insentif MORE'),
			('pencapaian_rekrutmen', 'Pencapaian Rekurtmen'),
			('grade_rekrutmen_id', 'Grade Rekrutmen'),
			('pencapaian_maintain', 'Pencapaian Maintain'),
			('grade_maintain_id', 'Grade Maintain'),
			('pencapaian_tl', 'Pencapaian TL'),
			('grade_tl_id', 'Grade TL'),
			('insentif_maintain', 'Insentif Aktif'),
			('insentif_rekrutmen', 'Insentif Rekrutmen'),
			('insentif_tl', 'Insentif TL'),
			('insentif_suffer', 'Insentif Wilayah Suffer'),
			('sum', 'SUM'),
			('insentif_total', 'Insentif Total'),
			('pemenuhan', 'Maintain'),
		]


	def _get_query_ro(self):
		_select = """
			SELECT
			 employee.name karyawan,
			 employee.id id_karyawan,
			 emkl.name name,
			 coalesce(emkl.absen, 0) absensi,
			 coalesce(emkl.tidak_masuk, 0) tidak_masuk,
			 coalesce(emkl.more, 0) more,
			 coalesce(emkl.cabang, 0) cabang,
			 coalesce(emkl.formasi, 0) formasi,
			 coalesce(emkl.aktif, 0) aktif,
			 coalesce(emkl.rekrutmen, 0) rekrutmen,
			 coalesce(emkl.tl, 0) tl,
			 coalesce(emkl.pencapaian_rekrutmen, 0) pencapaian_rekrutmen,
			 coalesce(emkl.pencapaian_maintain, 0) pencapaian_maintain,
			 coalesce(emkl.pencapaian_tl, 0) pencapaian_tl,
			 coalesce(emkl.pencapaian_average, 0) pencapaian_average,
			 emkl.grade_absen_id grade_absen_id,
			 emkl.grade_more_id grade_more_id,
			 emkl.grade_rekrutmen_id grade_rekrutmen_id,
			 emkl.grade_maintain_id grade_maintain_id,
			 emkl.grade_tl_id grade_tl_id,
			 emkl.grade_average_id grade_average_id,
			 coalesce(emkl.insentif_maintain, 0) insentif_maintain,
			 coalesce(emkl.insentif_rekrutmen, 0) insentif_rekrutmen,
			 coalesce(emkl.insentif_tl, 0) insentif_tl,
			 coalesce(emkl.potongan_absen, 0) potongan_absen,
			 coalesce(emkl.insentif_more, 0) insentif_more,
			 month.sequence sequence,
			 coalesce(emkl.formasi - emkl.aktif, 0) kurang
		"""

		_from = """
			FROM
			 employee_monthly_kpi_line emkl
			 left join hr_employee employee on (emkl.employee_id = employee.id)
			 left join res_month month on (emkl.month_id = month.id)
			 left join employee_ro_kpi ro on (emkl.employee_kpi_id = ro.id)
			 left join kpi_mekaar_batch kmb on (ro.kpi_mekaar_batch_id = kmb.id)
			 
		"""

		_where = """
			WHERE
			 kmb.id = %s
		"""

		_group = ""

		_order = "ORDER BY name, sequence"

		return _select, _from, _where, _group, _order
	
	def _get_sum_ro(self, result, employee, kpi_line):
		absensi = sum(r['absensi'] for r in result)
		more = sum(r['more'] for r in result)
		cabang = sum(r['cabang'] for r in result)
		formasi = sum(r['formasi'] for r in result)
		aktif = sum(r['aktif'] for r in result)
		rekrutmen = sum(r['rekrutmen'] for r in result)
		tl = sum(r['tl'] for r in result)
		kurang = sum(r['kurang'] for r in result)
		potongan_absen = sum(r['potongan_absen'] for r in result)
		insentif_more = sum(r['insentif_more'] for r in result)
		insentif_maintain = sum(r['insentif_maintain'] for r in result)
		insentif_rekrutmen = sum(r['insentif_rekrutmen'] for r in result)
		insentif_tl = sum(r['insentif_tl'] for r in result)
		insentif_suffer = kpi_line.filtered(lambda s:s.employee_id == employee).insentif_wilayah_suffer
		all_insentif = [potongan_absen, insentif_more, insentif_maintain, insentif_rekrutmen, insentif_tl, insentif_suffer]
		return {
			'name' : employee.name,
			'absensi' : absensi,
			'more' : more,
			'cabang' : cabang,
			'formasi' : formasi,
			'aktif' : aktif,
			'rekrutmen' : rekrutmen,
			'tl' : tl,
			'kurang' : max(kurang, 0),
			'potongan_absen' : potongan_absen,
			'insentif_more' : insentif_more,
			'insentif_maintain' : insentif_maintain,
			'insentif_rekrutmen' : insentif_rekrutmen,
			'insentif_tl' : insentif_tl,
			'insentif_suffer' : insentif_suffer,
			'sum' : sum(all_insentif),
			# 'insentif_total' : ,
			# 'pemenuhan' : ,
		}
	
	def _build_data_ro(self, results, obj):
		data = dict()
		employee_ids = obj.employee_ro_kpi_line.mapped('employee_id').ids
		for employee_id in employee_ids:
			employee = self.env['hr.employee'].browse(employee_id)
			result = list(filter(lambda s:s['id_karyawan'] == employee_id, results))
			
			data[employee_id] = {
				'total' : self._get_sum_ro(result, employee, obj.employee_ro_kpi_line)
			}

			data[employee_id]['data'] = [
				{
					'name' : r['name'],
					'absensi' : r['absensi'],
					'more' : r['more'],
					'cabang' : r['cabang'],
					'formasi' : r['formasi'],
					'aktif' : r['aktif'],
					'rekrutmen' : r['rekrutmen'],
					'tl' : r['tl'],
					'kurang' : max(r['kurang'], 0),
					'grade_absen_id' : self.env['grading.template'].browse(r['grade_absen_id']).grade,
					'potongan_absen' : r['potongan_absen'],
					'grade_more_id' : self.env['grading.template'].browse(r['grade_more_id']).grade,
					'insentif_more' : r['insentif_more'],
					'pencapaian_rekrutmen' : r['pencapaian_rekrutmen'],
					'grade_rekrutmen_id' : self.env['grading.template'].browse(r['grade_rekrutmen_id']).grade,
					'pencapaian_maintain' : r['pencapaian_maintain'],
					'grade_maintain_id' : self.env['grading.template'].browse(r['grade_maintain_id']).grade,
					'pencapaian_tl' : r['pencapaian_tl'],
					'grade_tl_id' : self.env['grading.template'].browse(r['grade_tl_id']).grade,
					'insentif_maintain' : r['insentif_maintain'],
					'insentif_rekrutmen' : r['insentif_rekrutmen'],
					'insentif_tl' : r['insentif_tl'],
					'pemenuhan' : min(r['formasi'] and r['aktif'] / r['formasi'] or 0, 1),
				} for r in result
			]
			# print(list(result))


		return data

	def _write_result(self, workbook, data_ro, obj):
		worksheet = workbook.add_worksheet()
		row = 5
		no = 1 
		col = 0
		HDR = self._get_header_ro()
		for f,label in HDR:
			worksheet.write(row, col, label, workbook.add_format({'bold': True, 'font_name' : 'Times New Roman', 'align' : 'center', 'border':1}))
			col += 1
		row +=1

		employee_ids = obj.employee_ro_kpi_line.mapped('employee_id')

		for employee in employee_ids:
			col = 0
			frmt = {'font_name' : 'Times New Roman', 'border' : 1, 'align' : 'center', 'bold' : True, 'bg_color' : '#8eb4e3'}
			total = data_ro[employee.id]['total']
			for f, label in HDR:
				val_to_write = total.get(f)
				if type(total.get(f)) is float:
					frmt.update({'num_format' : '_ * #,##0.00_) ;_ * - #,##0.00_) ;_ * "-"??_) ;_ @_', 'align' : 'right'})

				worksheet.write(row, col, val_to_write, workbook.add_format(frmt))
				col += 1
			row += 1


			# data_kpi = data_ro[employee.id]['data']
			# col = 1
			for line in data_ro[employee.id]['data']:
				frmt = {'font_name' : 'Times New Roman', 'border' : 1, 'align' : 'center'}
				# worksheet.write(row, 0, no, workbook.add_format(frmt))
				col = 0
				for f, label in HDR:
					frmt = frmt
					val_to_write = line.get(f)
					if type(line.get(f)) is dict:
						val_to_write = line.get(f).get(self._context.get('lang'))

					if 'pencapaian' in f:
						frmt.update({'num_format' : '0.00%'})
					elif type(line.get(f)) is float:
						frmt.update({'num_format' : '_ * #,##0.00_) ;_ * - #,##0.00_) ;_ * "-"??_) ;_ @_', 'align' : 'right'})

					worksheet.write(row, col, val_to_write, workbook.add_format(frmt))
					col += 1
				row += 1

	def generate_xlsx_report(self, workbook, data, obj):
		if len(obj) > 1:
			raise ValidationError(_("Hanya bisa cetak 1 data rekap saja."))
		# print(obj)
		# date_from = datetime.combine(obj.date_from, time(0,0))
		# date_to = datetime.combine(obj.date_to, time(23,59,59))

		arguments = [obj.id]

		_select, _from, _where, _group, _order = self._get_query_ro()
		
		query = ' '.join(x for x in [_select, _from, _where, _group, _order])
		self.env.cr.execute(query, arguments)
		results = self.env.cr.dictfetchall()
		data_ro = self._build_data_ro(results, obj)
		self._write_result(workbook, data_ro, obj)
		# # print(results)
		# if results:
		# 	self._write_result(workbook, results)

