from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError
from odoo.tools.misc import clean_context, format_date
import base64

class HrExpense(models.Model):
	_inherit = 'hr.expense.sheet'

	name = fields.Char(default='/')
	date = fields.Date(string='Date', default=lambda s:fields.Date.context_today(s))
	program_kerja_id = fields.Many2one(comodel_name='mum.program.kerja', string='Program Kerja')
	divisi_id = fields.Many2one(comodel_name='hr.department', string='Divisi', domain=[('divisi', '=', True)])
	anggaran_bulanan_divisi_id = fields.Many2one(comodel_name='anggaran.bulanan.divisi', string='Anggaran Bulanan Divisi')
	state = fields.Selection([
		('draft', 'Draft'),
		('submit', 'Approval 1'),
		('approval_1', 'Approval 2'),
		('approve', 'Approved'),
		('post', 'Posted'),
		('done', 'Done'),
		('cancel', 'Refused')
	], string='Status', index=True, readonly=True, tracking=True, copy=False, default='draft', required=True)
	wilayah = fields.Char(string='Wilayah')
	description = fields.Text(string='Notes')
	date_approve = fields.Datetime(string='Tanggal Approve')
	tipe_expense = fields.Selection([
		('petty_cash', 'Petty Cash'),
		('reimbursment', 'Reimbursment')
	], default='reimbursment', string="Tipe Pengajuan", copy=False)

	source_attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation="source_attachment_rel", string='Dokumen Reimbursment')
	has_invoice = fields.Boolean('Invoice')
	invoice_attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation="invoice_attachment_rel", string='Invoice / Kwitansi')
	has_faktur_npwp = fields.Boolean('Faktur Pajak &/ NPWP')
	faktur_attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation="faktur_attachment_rel", string='Faktur Pajak &/ NPWP')
	has_spk_pks = fields.Boolean('Invoice')
	spk_attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='SPK &/ PKS', relation='spk_attachment_rel')
	has_memo = fields.Boolean('Invoice')
	memo_attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Memo Persetujuan', relation='memo_attachment_rel')
	has_surat_penawaran = fields.Boolean('Invoice')
	surat_penawaran_attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Surat Penawaran', relation='penawaran_attachment_rel')
	has_form_pengadaan = fields.Boolean('Invoice')
	form_pengadaan_attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Form Pengadaan', relation='form_pengadaan_attachment_rel')
	has_tanda_terima = fields.Boolean('Invoice')
	tanda_terima_attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Tanda Terima / BAST', relation='tanda_terima_attachment_rel')
	has_no_rekening = fields.Boolean('Invoice')
	no_rekening_attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='No Rekening / Virtual Account', relation='rekening_attachment_rel')
	has_lainnya = fields.Boolean('Invoice')
	lainnya_attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Lainnya', relation='lainnya_attachment_rel')



	#CRUD METHOD
	@api.model
	def create(self,vals):
		if not vals.get('date'):
			raise ValidationError(_("Kolom Date harus diisi."))
		vals['name'] = self.env['ir.sequence'].next_by_code('expense.seq', fields.Date.to_date(vals.get('tgl_dibuat')))
		return super().create(vals)

	def write(self,vals):
		return super().write(vals)

	def unlink(self):
		return super().unlink()



	#LOGIC METHOD
	def approve_expense_sheets(self):
		self.button_render_document()
		self.write({
			'date_approve' : fields.Datetime.now(self),
		})
		super().approve_expense_sheets()

	def _do_create_moves(self):
		self = self.with_context(clean_context(self.env.context)) # remove default_*
		skip_context = {
			'skip_invoice_sync':True,
			'skip_invoice_line_sync':True,
			'skip_account_move_synchronization':True,
			'check_move_validity':False,
		}
		own_account_sheets = self.filtered(lambda sheet: sheet.payment_mode == 'own_account')
		company_account_sheets = self - own_account_sheets

		moves = self.env['account.move'].create([sheet._prepare_bill_vals() for sheet in own_account_sheets])
		payments = self.env['account.payment'].with_context(**skip_context).create([sheet._prepare_payment_vals() for sheet in company_account_sheets])
		moves |= payments.move_id
		# moves.action_post()

		self.activity_update()

		return moves
	
	def _prepare_bill_vals(self):
		vals = super()._prepare_bill_vals()
		vals.update({
			'program_kerja_id' : self.program_kerja_id.id,
			'source_attachment_ids' : self.source_attachment_ids,
			'has_invoice' : self.has_invoice,
			'move_invoice_attachment_ids' : self.invoice_attachment_ids,
			'has_faktur_npwp' : self.has_faktur_npwp,
			'move_faktur_attachment_ids' : self.faktur_attachment_ids,
			'has_spk_pks' : self.has_spk_pks,
			'move_spk_attachment_ids' : self.spk_attachment_ids,
			'has_memo' : self.has_memo,
			'move_memo_attachment_ids' : self.memo_attachment_ids,
			'has_surat_penawaran' : self.has_surat_penawaran,
			'move_surat_penawaran_attachment_ids' : self.surat_penawaran_attachment_ids,
			'has_form_pengadaan' : self.has_form_pengadaan,
			'move_form_pengadaan_attachment_ids' : self.form_pengadaan_attachment_ids,
			'has_tanda_terima' : self.has_tanda_terima,
			'move_tanda_terima_attachment_ids' : self.tanda_terima_attachment_ids,
			'has_no_rekening' : self.has_no_rekening,
			'move_no_rekening_attachment_ids' : self.no_rekening_attachment_ids,
			'has_lainnya' : self.has_lainnya,
			'move_lainnya_attachment_ids' : self.lainnya_attachment_ids,
		})
		return vals
	@api.onchange('date', 'divisi_id')
	def _onchange_anggaran_bulanan(self):
		self.anggaran_bulanan_divisi_id = False
		if self.date and self.divisi_id:
			month_id = self.env['res.month'].search([('sequence', '=', self.date.strftime('%m'))], limit=1)
			thn = self.date.strftime('%Y')
			self.anggaran_bulanan_divisi_id = self.env['anggaran.bulanan.divisi'].search([('divisi_id', '=', self.divisi_id.id), ('month_id', '=', month_id.id), ('tahun', '=', thn)], limit=1).id

	@api.onchange('employee_id')
	def _onchange_karyawan(self):
		self.divisi_id = False
		if self.employee_id:
			self.divisi_id = self.employee_id.department_id.divisi and self.employee_id.department_id.id or self.employee_id.department_id.parent_id.id

	def _do_approve(self):
		notification = super()._do_approve()
		self.write({'state' : 'approve'})
		return notification
	
	# @api.depends_context('uid')
	# @api.depends('employee_id')
	def _compute_can_approve(self):
		# is_approver = self.user_has_groups('hr_expense.group_hr_expense_team_approver, hr_expense.group_hr_expense_user')
		# is_manager = self.user_has_groups('hr_expense.group_hr_expense_manager')
		for sheet in self:
			# sheet.can_approve = is_manager or (is_approver and sheet.employee_id.user_id != self.env.user)
			sheet.can_approve = False
			if sheet.state == 'submit' and sheet.user_id == self.env.user:
				sheet.can_approve = True
			elif sheet.state == 'approval_1' and sheet.divisi_id.manager_id.user_id == self.env.user:
				sheet.can_approve = True

	def create_doc_attachment(self):
		report = self.env['ir.actions.report']._render_qweb_pdf(report_ref='hr_expense.action_report_hr_expense_sheet', res_ids=self.ids)

		# Simpan biner PDF
		pdf_biner = report[0]
		# print(pdf_biner)

		# Nama file PDF
		pdf_name = f"Reimbursment_{self.name}.pdf"

		# Membuat attachment baru
		attachment = self.env['ir.attachment'].create({
			'name': pdf_name,
			'type': 'binary',
			'datas': base64.b64encode(pdf_biner),
			'res_model': 'hr.expense.sheet',
			'res_id': self.id,
			'mimetype': 'application/pdf',
		})
		# print(attachment)

		return attachment, pdf_biner

	#BUTTON METHOD
	def button_render_document(self):
		attachment, pdf_biner = self.create_doc_attachment()
		# self._message_post_process_attachments(attachments=pdf_biner, attachment_ids=attachment.ids, message_values='test')
		# print(attachment)
		# self.write({
		# 	'attachment_ids' : [Command.link(attachment.id)]
		# })
		# self.attachment_ids = attachment
		# print(self.attachment_ids)
		# self.message_post(attachments=pdf_biner,attachment_ids=[attachment.id])
		# print(attachment)
		self.source_attachment_ids = attachment
	
	def button_approve_1(self):
		# Kadiv
		self.write({'state' : 'approval_1'})

	# def button_approve_2(self):
	# 	self.write({'state' : 'approval_2'})



	#ACTION METHOD

class HrExpense(models.Model):
	_inherit = 'hr.expense'

	program_kerja_id = fields.Many2one(comodel_name='mum.program.kerja', string='Program Kerja')



	#CRUD METHOD
	@api.model
	def create(self,vals):
		return super().create(vals)

	def write(self,vals):
		return super().write(vals)

	def unlink(self):
		return super().unlink()



	#LOGIC METHOD
	def _convert_to_tax_base_line_dict(self, base_line=None, currency=None, price_unit=None, quantity=None):
		self.ensure_one()
		return self.env['account.tax']._convert_to_tax_base_line_dict(
			base_line,
			currency=currency or self.currency_id,
			product=self.product_id,
			taxes=self.tax_ids,
			price_unit=price_unit or self.total_amount_company,
			quantity=quantity or 1,
			account=self.account_id,
			analytic_distribution=self.analytic_distribution,
			extra_context={'force_price_include': False},
		)

	def _get_taxes(self, price, quantity):
		# Deprecated
		self.ensure_one()
		return self.tax_ids.with_context(force_price_include=False, round=True) \
			.compute_all(price, self.currency_id, quantity, self.product_id, self.employee_id.user_id.partner_id)



	#BUTTON METHOD



	#ACTION METHOD

