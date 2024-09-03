from odoo import _, api, fields, models, Command


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # user_create_id = fields.Many2one(comodel_name='res.users', string='Diajukan Oleh', default=lambda s:s.env.user.id)
    name = fields.Char(tracking=True)
    team_id = fields.Many2one(tracking=True)
    category_id = fields.Many2one(tracking=True)
    description = fields.Text('Description', tracking=True)
    helpdesk_attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Attachments')
    perihal = fields.Text('Perihal', tracking=True)
    readonly = fields.Boolean('Readonly', compute='_compute_readonly')
    stage_sequence = fields.Integer(string='Stage Sequence', related='stage_id.sequence')
    catatan_tim = fields.Text(string='Catatan Tim', tracking=True)
    partner_id = fields.Many2one(default=lambda s:s.env.user.partner_id.id)
    user_ids = fields.Many2many(related="category_id.user_ids")
    team_user = fields.Boolean(compute='_compute_team_user')
    add_attachment = fields.Boolean()
    has_attachment = fields.Boolean(compute='_compute_has_attachment')

    #CRUD METHOD
    @api.model
    def create(self,vals):
        return super().create(vals)

    def write(self,vals):
        return super().write(vals)

    def unlink(self):
        return super().unlink()



    #LOGIC METHOD
    @api.depends('helpdesk_attachment_ids', 'add_attachment')
    def _compute_has_attachment(self):
        for rec in self:
            rec.has_attachment = rec.helpdesk_attachment_ids or rec.add_attachment
            
    def _compute_team_user(self):
        for rec in self:
            rec.team_user = self.env.user.id in rec.user_ids.ids or self.user_has_groups('helpdesk_mgmt.group_helpdesk_user')

    @api.depends('stage_id')
    def _compute_readonly(self):
        for rec in self:
            rec.readonly = rec.stage_id.readonly

    @api.onchange('category_id')
    def _onchange_category_id(self):
        self.team_id = self.category_id and self.category_id.team_id or False



    #BUTTON METHOD
    def button_add_attachment(self):
        self.add_attachment = True

    """
        staging sequence:
        baru                    = 1
        sedang diproses         = 2
        menunggu konfirmasi     = 3
        selsai                  = 100
        revisi                  = 200
        ditolak                 = 999
    """
    def button_selesai(self):
        stage_id = self.env['helpdesk.ticket.stage'].search([('sequence', '=', 100)], limit=1)
        self.write({'stage_id' : stage_id.id})

    def button_revisi(self):
        stage_id = self.env['helpdesk.ticket.stage'].search([('sequence', '=', 200)], limit=1)
        self.write({'stage_id' : stage_id.id})

    def button_reject(self):
        stage_id = self.env['helpdesk.ticket.stage'].search([('sequence', '=', 999)], limit=1)
        self.write({'stage_id' : stage_id.id})

    def button_confirm(self):
        stage_id = self.env['helpdesk.ticket.stage'].search([('sequence', '=', 3)], limit=1)
        self.write({'stage_id' : stage_id.id})





    #ACTION METHOD
