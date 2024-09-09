from odoo import _, api, fields, models, Command

class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    planned_amount = fields.Monetary('Planned Amount')
    practical_amount = fields.Monetary('Practical Amount', compute='_compute_practical_amount')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', related='company_id.currency_id')
    budget_parent_ids = fields.One2many(comodel_name='account.budget.parent', inverse_name='crossovered_budget_id', string='Budget Parents')
    anggaran_divisi_ids = fields.One2many(comodel_name='anggaran.divisi', inverse_name='crossovered_budget_id', string='Anggaran Divisi')
    anggaran_bulanan_divisi_ids = fields.One2many(comodel_name='anggaran.bulanan.divisi', inverse_name='crossovered_budget_id', string='Angggaran Bulanan Divisi')



    #CRUD METHOD
    @api.model
    def create(self,vals):
        return super().create(vals)

    def write(self,vals):
        return super().write(vals)

    def unlink(self):
        return super().unlink()



    #LOGIC METHOD
    def _compute_practical_amount(self):
        for rec in self:
            rec.practical_amount = sum(l.practical_amount for l in rec.budget_parent_ids)



    #BUTTON METHOD



    #ACTION METHOD



class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    budget_parent_id = fields.Many2one(comodel_name='account.budget.parent', string='Budget Parent')



    #CRUD METHOD
    @api.model
    def create(self,vals):
        return super().create(vals)

    def write(self,vals):
        return super().write(vals)

    def unlink(self):
        return super().unlink()



    #LOGIC METHOD



    #BUTTON METHOD



    #ACTION METHOD
