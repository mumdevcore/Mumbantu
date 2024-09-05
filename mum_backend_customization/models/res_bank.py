from odoo import _, api, fields, models, Command


class ResBank(models.Model):
    _inherit = 'res.bank'

    domestic_bank = fields.Char(string='Domestic Bank')
    online_code = fields.Char(string='Online Bank Code')



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
