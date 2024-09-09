# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, Command, _
from datetime import datetime, time, date
from pprint import pprint
from odoo.tools import html2plaintext
from odoo.exceptions import ValidationError
import pandas as pd

class LaporanPenjualanPosPerItemXlsx(models.AbstractModel):
	_name = 'report.mum_budget.memo_pembayaran_invoice_xlsx'
	_inherit = 'report.report_xlsx.abstract'
	_description = 'Laporan Penjualan POS Xlsx'

	def _prepare_header(self):
		return [
			('no_rekening', 'No. Rekening'),
			('nama_rekening', 'Nama Rekening'),
			('nominal', 'Nominal'),
			('keterangan', 'Keterangan'),
			('kode_clearing', 'Kode Clearing'),
			('nama_bank', 'Nama Bank'),
			# ('remark', 'Remark'),
			('email', 'Email')
		]
	
	# def _write_result(self, workbook, results):
		worksheet = workbook.add_worksheet()
		row = no = col = 1
		col = 1
		HDR = self._prepare_header()
		worksheet.write(row, 0, 'No', workbook.add_format({'bold': True, 'font_name' : 'Times New Roman', 'align' : 'center', 'border':1}))
		for f,label in HDR:
			worksheet.write(row, col, label, workbook.add_format({'bold': True, 'font_name' : 'Times New Roman', 'align' : 'center', 'border':1}))
			col += 1
		row +=1
		for line in pos_orders:
			frmt = {'font_name' : 'Times New Roman', 'border' : 1, 'align' : 'center'}
			worksheet.write(row, 0, no, workbook.add_format(frmt))
			col = 1
			for f, label in HDR:
				frmt = frmt
				val_to_write = line.get(f)
				if type(line.get(f)) is dict:
					val_to_write = line.get(f).get(self._context.get('lang'))

				if f == 'harga_no_ppn' and line.get('order_line'):
					order_line_id = self.env['pos.order.line'].browse(line.get('order_line'))
					harga_non_ppn = order_line_id.tax_ids_after_fiscal_position.compute_all(line.get('jumlah'), product=order_line_id.product_id, partner=self.env['res.partner'])
					val_to_write = harga_non_ppn['total_excluded']

				if type(line.get(f)) is float:
					if f in ['harga', 'diskon', 'jumlah', 'harga_no_ppn', 'dpp', 'unit_cost', 'total_hpp', 'laba', 'pajak', 'total_harga', 'nominal']:
						frmt.update({'num_format' : '[$Rp-421]#,##0.00', 'align' : 'right'})
					else:
						frmt.update({'num_format' : '_ * #,##0.00_) ;_ * - #,##0.00_) ;_ * "-"??_) ;_ @_', 'align' : 'right'})
				elif type(line.get(f)) is date:
					frmt.update({'num_format' : 'dd/mm/yy', 'align' : 'center'})
				elif type(line.get(f)) is datetime:
					frmt.update({'num_format' : 'dd/mm/yy', 'align' : 'center'})
				elif type(line.get(f)) is pd.Timestamp:
					frmt.update({'num_format' : 'dd/mm/yy', 'align' : 'center'})
				
				worksheet.write(row, col, val_to_write, workbook.add_format(frmt))
				col += 1

			no += 1
			row += 1

	def _prepare_values(self, obj):
		values = []
		for invoice in obj.invoice_ids:
			values.append({
				'no_rekening' : invoice.partner_bank_id.acc_number,
				'nama_rekening' : invoice.partner_bank_id.acc_holder_name,
				'nominal' : invoice.amount_total,
				'keterangan' : html2plaintext(invoice.narration),
				'kode_clearing' : invoice.partner_bank_id.bank_id.domestic_bank,
				'nama_bank' : invoice.partner_bank_id.bank_id.name,
				# 'remark' : '',
				'email' : invoice.partner_id.email,
			})

		return values
			
	def generate_xlsx_report(self, workbook, data, obj):
		worksheet = workbook.add_worksheet()
		row = no = col = 1
		col = 1
		HDR = self._prepare_header()
		worksheet.write(row, 0, 'No', workbook.add_format({'bold': True, 'font_name' : 'Times New Roman', 'align' : 'center', 'border':1}))
		for f,label in HDR:
			worksheet.write(row, col, label, workbook.add_format({'bold': True, 'font_name' : 'Times New Roman', 'align' : 'center', 'border':1}))
			col += 1
		row +=1
		values = self._prepare_values(obj)
		for line in values:
			frmt = {'font_name' : 'Times New Roman', 'border' : 1, 'align' : 'center'}
			worksheet.write(row, 0, no, workbook.add_format(frmt))
			col = 1
			for f, label in HDR:
				frmt = frmt
				val_to_write = line.get(f)
				if type(line.get(f)) is dict:
					val_to_write = line.get(f).get(self._context.get('lang'))

				if f == 'harga_no_ppn' and line.get('order_line'):
					order_line_id = self.env['pos.order.line'].browse(line.get('order_line'))
					harga_non_ppn = order_line_id.tax_ids_after_fiscal_position.compute_all(line.get('jumlah'), product=order_line_id.product_id, partner=self.env['res.partner'])
					val_to_write = harga_non_ppn['total_excluded']

				if type(line.get(f)) is float:
					if f in ['harga', 'diskon', 'jumlah', 'harga_no_ppn', 'dpp', 'unit_cost', 'total_hpp', 'laba', 'pajak', 'total_harga', 'nominal']:
						frmt.update({'num_format' : '[$Rp-421]#,##0.00', 'align' : 'right'})
					else:
						frmt.update({'num_format' : '_ * #,##0.00_) ;_ * - #,##0.00_) ;_ * "-"??_) ;_ @_', 'align' : 'right'})
				elif type(line.get(f)) is date:
					frmt.update({'num_format' : 'dd/mm/yy', 'align' : 'center'})
				elif type(line.get(f)) is datetime:
					frmt.update({'num_format' : 'dd/mm/yy', 'align' : 'center'})
				elif type(line.get(f)) is pd.Timestamp:
					frmt.update({'num_format' : 'dd/mm/yy', 'align' : 'center'})
				
				worksheet.write(row, col, val_to_write, workbook.add_format(frmt))
				col += 1

			no += 1
			row += 1