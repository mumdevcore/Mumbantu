from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError


class AccountBudgetParent(models.Model):
	_name = 'account.budget.parent'
	_description = 'Account Budget Parent'
	# _rec_name = 'general_budget_id'

	name = fields.Char(string='Name')
	general_budget_id = fields.Many2one(comodel_name='account.budget.post', string='Budget Position')
	crossovered_budget_id = fields.Many2one(comodel_name='crossovered.budget', string='Budget Tahunan')
	crossovered_budget_child_ids = fields.One2many(comodel_name='crossovered.budget.lines', inverse_name='budget_parent_id', string='Budget Parent')
	currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
	planned_amount = fields.Monetary('Planned Amount', required=True,help="Amount you plan to earn/spend. Record a positive amount if it is a revenue and a negative amount if it is a cost.", compute='_compute_planned_amount')
	practical_amount = fields.Monetary(string='Practical Amount', help="Amount really earned/spent.", compute='_compute_practical_amount')
	theoritical_amount = fields.Monetary(string='Theoretical Amount',help="Amount you are supposed to have earned/spent at this date.")
	percentage = fields.Float(string='Achievement', help="Comparison between practical and theoretical amount. This measure tells you if you are below or over budget.")
	company_id = fields.Many2one(related='crossovered_budget_id.company_id', comodel_name='res.company', string='Company', store=True, readonly=True)



	#CRUD METHOD
	@api.model
	def create(self,vals):
		return super().create(vals)

	def write(self,vals):
		return super().write(vals)

	def unlink(self):
		return super().unlink()
	
	@api.constrains('crossovered_budget_id.planned_amount', 'planned_amount')
	def _check_crossovered_budget_id(self):
		# CODE HERE
		if sum(x.planned_amount for x in self) > self.crossovered_budget_id.planned_amount:
			raise ValidationError(_("Anggaran terlalu besar"))



	#LOGIC METHOD
	# def _compute_planned_amount(self):
	# 	for rec in self:
	# 		rec.planned_amount = sum(l.planned_amount for l in rec.crossovered_budget_child_ids)

	def _compute_practical_amount(self):
		for rec in self:
			rec.practical_amount = sum(l.practical_amount for l in rec.crossovered_budget_child_ids)



	#BUTTON METHOD



	#ACTION METHOD
	def action_show_details(self):
		self.ensure_one()
		# tree_view = self.env.ref('mum_kpi.employee_kpi_view_tree')
		form_view = self.env.ref('mum_budget.account_budget_parent_view_form')
		# pivot_view = self.env.ref('mum_kpi.employee_kpi_view_pivot')
		return {
			'name': _('Budget Parent'),
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'account.budget.parent',
			'views': [(form_view.id, 'form')],
			'view_id': form_view.id,
			'target': 'new',
			'res_id' : self.id,
			# 'domain' : [('id', 'in', self.employee_kpi_line.ids)]
		}
