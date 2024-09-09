from odoo import _, api, fields, models, Command


class ProgramKerja(models.Model):
    _name = 'mum.program.kerja'
    _description = 'Program Kerja'

    name = fields.Char(string='')
    divisi_id = fields.Many2one(comodel_name='hr.department', string='Divisi', domain=[('divisi', '=', True)])



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
