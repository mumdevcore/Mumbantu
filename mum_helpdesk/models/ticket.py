from odoo import _, api, fields, models, Command


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # user_create_id = fields.Many2one(comodel_name='res.users', string='Diajukan Oleh', default=lambda s:s.env.user.id)
    helpdesk_attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Attachments')
    perihal = fields.Text('Perihal')
    readonly = fields.Boolean('Readonly', compute='_compute_readonly')
    partner_id = fields.Many2one(default=lambda s:s.env.user.partner_id.id)

    #CRUD METHOD
    @api.model
    def create(self,vals):
        return super().create(vals)

    def write(self,vals):
        return super().write(vals)

    def unlink(self):
        return super().unlink()



    #LOGIC METHOD
    @api.depends('stage_id')
    def _compute_readonly(self):
        for rec in self:
            rec.readonly = rec.stage_id.readonly

    @api.onchange('category_id')
    def _onchange_category_id(self):
        self.team_id = self.category_id and self.category_id.team_id or False



    #BUTTON METHOD



    #ACTION METHOD
