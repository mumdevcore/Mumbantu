from odoo import _, api, fields, models, Command


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    helpdesk_attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Attachments')
    perihal = fields.Text('Perihal')

    #CRUD METHOD
    @api.model
    def create(self,vals):
        return super().create(vals)

    def write(self,vals):
        return super().write(vals)

    def unlink(self):
        return super().unlink()



    #LOGIC METHOD
    @api.onchange('category_id')
    def _onchange_category_id(self):
        self.team_id = self.category_id and self.category_id.team_id or False



    #BUTTON METHOD



    #ACTION METHOD
