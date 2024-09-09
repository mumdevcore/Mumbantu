from odoo import _, api, fields, models, Command
from odoo.tools.misc import frozendict
from pprint import pprint

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	# name = fields.Char(string='')
	nominal_anggaran_bulanan = fields.Monetary(string='Nominal Anggaran Bulanan')
	sisa_anggaran_bulanan = fields.Monetary(string='Sisa Anggaran Bulanan')
	nominal_anggaran_tahunan = fields.Monetary(string='Nominal Anggaran Tahunan')
	sisa_anggaran_tahunan = fields.Monetary(string='Sisa Anggaran Tahunan')



	#CRUD METHOD
	@api.model
	def create(self,vals):
		return super().create(vals)

	def write(self,vals):
		return super().write(vals)

	def unlink(self):
		return super().unlink()



	#LOGIC METHOD
	def _convert_to_tax_base_line_dict(self):
		result = super()._convert_to_tax_base_line_dict()
		if self.expense_id:
			result.setdefault('extra_context', {})
			result['extra_context']['force_price_include'] = False
		return result
	
	# def _compute_all_tax(self):
	# 	expense_lines = self.filtered('expense_id')
	# 	super(AccountMoveLine, expense_lines.with_context(force_price_include=False))._compute_all_tax()
	# 	super(AccountMoveLine, self - expense_lines)._compute_all_tax()
	# 	for line in expense_lines:
	# 		for key in list(line.compute_all_tax.keys()):
	# 			new_key = frozendict(**key, expense_id=line.expense_id.id)
	# 			line.compute_all_tax[new_key] = line.compute_all_tax.pop(key)

	def _compute_totals(self):
		expenses = self.filtered('expense_id')
		super(AccountMoveLine, expenses.with_context(force_price_include=False))._compute_totals()
		super(AccountMoveLine, self - expenses)._compute_totals()



	#BUTTON METHOD



	#ACTION METHOD
