from odoo import _, api, fields, models, Command
from pprint import pprint
from odoo.tools.float_utils import float_compare

class AccountMove(models.Model):
	_inherit = 'account.move'

	jenis_form = fields.Selection([
		('uang_muka', 'Uang Muka'),
		('laporan_pertanggungjawaban', 'Laporan Pertanggungjawaban'),
		('reimbursment', 'Reimbursment'),
	], string='Jenis Form Ceklist')
	source_attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation="move_source_attachment_rel", string='Dokumen Reimbursment')
	has_invoice = fields.Boolean('Invoice')
	move_invoice_attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation="move_invoice_attachment_rel", string='Invoice / Kwitansi')
	has_faktur_npwp = fields.Boolean('Faktur Pajak &/ NPWP')
	move_faktur_attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation="move_faktur_attachment_rel", string='Faktur Pajak &/ NPWP')
	has_spk_pks = fields.Boolean('Invoice')
	move_spk_attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='SPK &/ PKS', relation='move_spk_attachment_rel')
	has_memo = fields.Boolean('Invoice')
	move_memo_attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Memo Persetujuan', relation='move_memo_attachment_rel')
	has_surat_penawaran = fields.Boolean('Invoice')
	move_surat_penawaran_attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Surat Penawaran', relation='move_penawaran_attachment_rel')
	has_form_pengadaan = fields.Boolean('Invoice')
	move_form_pengadaan_attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Form Pengadaan', relation='move_form_pengadaan_attachment_rel')
	has_tanda_terima = fields.Boolean('Invoice')
	move_tanda_terima_attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Tanda Terima / BAST', relation='move_tanda_terima_attachment_rel')
	has_no_rekening = fields.Boolean('Invoice')
	move_no_rekening_attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='No Rekening / Virtual Account', relation='move_rekening_attachment_rel')
	has_lainnya = fields.Boolean('Invoice')
	move_lainnya_attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Lainnya', relation='move_lainnya_attachment_rel')
	state = fields.Selection(selection=[
			('draft', 'Draft'),
			('pajak', 'Pajak'),
			('anggaran', 'Anggaran'),
			('kabag', 'Kabag'),
			('kadiv', 'Kadiv'),
			('posted', 'Posted'),
			('cancel', 'Cancelled'),
		], string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft',)
	memo_pembayaran_id = fields.Many2one(comodel_name='memo.pembayaran', string='Memo Pembayaran')

	bukti_transfer_attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation="bukti_transfer_invoice_attachment_rel", string='Bukti Transfer')
	

	# KOLOM UNTUK DATA2 ANGGARAN
	program_kerja_id = fields.Many2one(comodel_name='mum.program.kerja', string='Program Kerja')
	nomor_anggaran = fields.Char(string='Nomor Anggaran')
	nominal_anggaran = fields.Monetary('Nominal Anggaran')
	sisa_anggaran = fields.Monetary('Sisa Anggaran')
	

	# KOLOM DATA2 UNTUK PAJAK
	dpp = fields.Monetary(string='DPP', compute='_compute_verifikasi_pajak')
	ppn = fields.Monetary(string='PPN', compute='_compute_verifikasi_pajak')
	dpp_ppn = fields.Monetary(string='DPP + PPN', compute='_compute_verifikasi_pajak')
	materai = fields.Monetary(string='Materai', compute='_compute_verifikasi_pajak')
	not_dpp = fields.Monetary(string='Bukan Unsur DPP', compute='_compute_verifikasi_pajak')
	total_tagihan = fields.Monetary(string='Total Tagihan', compute='_compute_verifikasi_pajak')
	pph = fields.Monetary(string='PPh', compute='_compute_verifikasi_pajak')
	uang_muka = fields.Monetary(string='Uang Muka', compute='_compute_verifikasi_pajak')
	ppn_wapu = fields.Monetary(string='PPN WAPU', compute='_compute_verifikasi_pajak')

	lampiran_invoice_ids = fields.One2many(comodel_name='lampiran.invoice', inverse_name='move_id', string='Lampiran Dokumen Pendukung')

	# INFORMASI ANGGARAN
	anggaran_bulanan_line_ids = fields.One2many(
		'account.move.line',
		'move_id',
		string='Anggaran Bulanan',
		copy=False,
		domain=[('display_type', 'in', ('product', 'line_section', 'line_note'))],
	)
	anggaran_bulanan_selection = fields.Selection([
		('within_budgeted', 'Within Budgeted'),
		('over_budgeted', 'Over Budgeted'),
		('non_budgeted', 'Non Budgeted'),
	], string="Status Anggaran")
	note_anggaran_bulanan = fields.Char(string='Komentar/Alasan')

	anggaran_tahunan_line_ids = fields.One2many(
		'account.move.line',
		'move_id',
		string='Anggaran Tahunan',
		copy=False,
		domain=[('display_type', 'in', ('product', 'line_section', 'line_note'))],
	)
	anggaran_tahunan_selection = fields.Selection([
		('within_budgeted', 'Within Budgeted'),
		('over_budgeted', 'Over Budgeted'),
		('non_budgeted', 'Non Budgeted'),
	], string="Status Anggaran")
	note_anggaran_tahunan = fields.Char(string='Komentar/Alasan')

	# KETERANGAN TROPS
	trops_selection = fields.Selection([
		('dapat_dibayar', 'Dapat Dibayar'),
		('ditunda', 'Pemb Ditunda'),
		('tdk_dibayar', 'Tdk Dapat Dibayar'),
		('sudah_dibayar', 'Sudah Dibayar'),
		], string="Status Trops")
	note_trops = fields.Char(string='Komentar/Alasan')
	tgl_dibayar = fields.Date(string='Tgl Dibayar') # Terisi ketika memo pembayaran sudah divalidasi.

	
	


	#CRUD METHOD
	@api.model
	def create(self,vals):
		lampiran_vals = self.env[self._name]._create_lampiran_dokumen_pendukung()

		print("Createeeeeeeeeeeeeeeeeeeeeeee")
		print(self)
		vals['lampiran_invoice_ids'] = lampiran_vals
		return super().create(vals)

	def write(self,vals):
		return super().write(vals)

	def unlink(self):
		return super().unlink()



	#LOGIC METHOD
	def _create_lampiran_dokumen_pendukung(self):
		template_lampiran_dokumen_ids = self.env['template.lampiran.invoice'].search([], order='sequence')
		lampiran_vals = [Command.create({
			'sequence' : t.sequence,
			'name' : t.name
		}) for t in template_lampiran_dokumen_ids]
		return lampiran_vals
			
			

	@api.depends('invoice_line_ids')
	def _compute_verifikasi_pajak(self):
		for move in self:
			# dpp = 
			line_with_tax_ids = move.invoice_line_ids.filtered(lambda l:l.tax_ids)
			line_without_tax_ids = move.invoice_line_ids.filtered(lambda l:not l.tax_ids)
			grup_ppn_id = self.env['account.tax.group'].search([('name', '=', 'PPN')], limit=1).id
			group_pph_id = self.env['account.tax.group'].search([('name', '=', 'PPH')], limit=1).id
			group_wapu_id = self.env['account.tax.group'].search([('name', '=', 'WAPU')], limit=1).id
			tax_dict = move.tax_totals['groups_by_subtotal']['Untaxed Amount']
			ppn = sum(tax.get('tax_group_amount') for tax in list(filter(lambda x:x['tax_group_id'] == grup_ppn_id, tax_dict)))
			pph = sum(tax.get('tax_group_amount') for tax in list(filter(lambda x:x['tax_group_id'] == group_pph_id, tax_dict)))
			wapu = sum(tax.get('tax_group_amount') for tax in list(filter(lambda x:x['tax_group_id'] == group_wapu_id, tax_dict)))

			move.dpp = sum(line_with_tax_ids.mapped('price_subtotal'))
			move.ppn = ppn
			move.dpp_ppn = move.dpp + move.ppn
			move.materai = 0
			move.not_dpp = sum(line_without_tax_ids.mapped('price_subtotal'))
			move.total_tagihan = move.dpp_ppn + move.not_dpp
			move.pph = pph
			move.uang_muka = 0
			move.ppn_wapu = wapu or 0

	@api.depends('date', 'auto_post')
	def _compute_hide_post_button(self):
		for record in self:
			record.hide_post_button = record.state != 'kadiv' or record.auto_post != 'no' and record.date > fields.Date.context_today(record)

	@api.depends('restrict_mode_hash_table', 'state')
	def _compute_show_reset_to_draft_button(self):
		for move in self:
			move.show_reset_to_draft_button = not move.restrict_mode_hash_table and move.state in ('pajak', 'anggaran', 'kabag', 'kadiv','posted', 'cancel')

	def _prepare_memo_pembayaran_vals(self, *args):
		vals = []
		for move in list(filter(lambda m:m, args)):
			# if move:
			vals.append({
				'tanggal' : fields.Date.context_today(move),
				'invoice_ids' : move
			})

		return vals



	#BUTTON METHOD
	def button_pajak(self):
		self.write({'state': 'pajak'})

	def button_anggaran(self):
		self.write({'state': 'anggaran'})

	def button_kabag(self):
		self.write({'state': 'kabag'})

	def button_kadiv(self):
		self.write({'state': 'kadiv'})



	#ACTION METHOD
	def action_memo_pembayaran(self):
		limit = self.env['ir.config_parameter'].sudo().get_param('mum_budget.default_limit_memo_pembayaran')
		moves = self.filtered(lambda m:m.state == 'posted' and m.payment_state != 'paid')
		move_in_limit = moves.filtered(lambda m:float_compare(m.amount_total, float(limit), precision_rounding=m.currency_id.rounding) < 0)
		move_more_than_limit = moves.filtered(lambda m:float_compare(m.amount_total, float(limit), precision_rounding=m.currency_id.rounding) > 0)
		memo_vals = self._prepare_memo_pembayaran_vals(move_in_limit, move_more_than_limit)
		memo_pembayaran_ids = self.env['memo.pembayaran'].create(memo_vals)
		action = self.env["ir.actions.actions"]._for_xml_id("mum_budget.action_memo_pembayaran")
		action['domain'] = [('id', 'in', memo_pembayaran_ids.ids)]
		return action
