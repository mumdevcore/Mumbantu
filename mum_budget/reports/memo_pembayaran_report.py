from odoo import _, api, fields, models, Command
from PyPDF2 import PdfFileReader, PdfFileWriter
import io


class ReportMemoPembayaran(models.AbstractModel):
	_name = 'report.mum_budget.memo_pembayaran_report_combine'
	
	#LOGIC METHOD
	@api.model
	def _get_report_values(self, docids, data=None):
		report_obj = self.env['ir.actions.report']
 
		pdf_portrait = report_obj._render_qweb_pdf('mum_budget.action_report_memo_pembayaran', docids, data)[0]
		pdf_landscape = report_obj._render_qweb_pdf('mum_budget.action_memo_pembayaran_report_detail', docids, data)[0]
		print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
		# print(pdf_portrait)

		# pdf_portrait = pdf_a.report_action(docids).get('pdf_content')
		# print("pdf_a.report_action(docids).get('pdf_content') ---- " , pdf_portrait)
		# pdf_landscape = pdf_b.report_action(docids).get('pdf_content')

		
		# Menggunakan PyPDF2 untuk menggabungkan PDF
		output = PdfFileWriter()

		# Membaca PDF pertama
		pdf_portrait_stream = io.BytesIO(pdf_portrait)
		pdf_landscape_stream = io.BytesIO(pdf_landscape)
		
		pdf_reader_portrait = PdfFileReader(pdf_portrait_stream)
		pdf_reader_landscape = PdfFileReader(pdf_landscape_stream)

		# Menambahkan halaman dari PDF pertama (portrait)
		for page in range(pdf_reader_portrait.getNumPages()):
			output.addPage(pdf_reader_portrait.getPage(page))

		# Menambahkan halaman dari PDF kedua (landscape)
		for page in range(pdf_reader_landscape.getNumPages()):
			output.addPage(pdf_reader_landscape.getPage(page))

		# Menghasilkan output sebagai PDF
		output_stream = io.BytesIO()
		output.write(output_stream)
		output_stream.seek(0)
		# print(output_stream)

		# Mengembalikan hasil sebagai file PDF gabungan
		return {
            'pdf_content': output_stream.getvalue(),
            'file_name': 'combined_report.pdf'
        }