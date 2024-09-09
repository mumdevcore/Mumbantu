from odoo import _, api, fields, models, Command


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    name = fields.Char(string='')



    #CRUD METHOD
    @api.model
    def create(self,vals):
        return super().create(vals)

    def write(self,vals):
        return super().write(vals)

    def unlink(self):
        return super().unlink()



    #LOGIC METHOD
    def _create_payments(self):
        paid_invoices = self.line_ids.move_id.write({'trops_selection' : 'sudah_dibayar', 'tgl_dibayar' : fields.Date.context_today(self)})

        return super()._create_payments()



    #BUTTON METHOD



    #ACTION METHOD
