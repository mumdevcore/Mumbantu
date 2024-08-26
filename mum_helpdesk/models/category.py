from odoo import _, api, fields, models, Command


class HelpdeskTicketCategory(models.Model):
    _inherit = 'helpdesk.ticket.category'

    team_id = fields.Many2one(comodel_name='helpdesk.ticket.team', string='Tim')
    filtered_user_ids = fields.Many2many(comodel_name='res.users', relation="helpdesk_categ_filtered_user_rel", string='Filtered Users', related='team_id.user_ids')
    user_ids = fields.Many2many(comodel_name='res.users', string='Penanggung Jawab',)




    #CRUD METHOD
    @api.model
    def create(self,vals):
        return super().create(vals)

    def write(self,vals):
        return super().write(vals)

    def unlink(self):
        return super().unlink()



    #LOGIC METHOD
    @api.onchange("team_id")
    def _onchange_team_id(self):
        self.user_ids = self.team_id.user_ids or False



    #BUTTON METHOD



    #ACTION METHOD
