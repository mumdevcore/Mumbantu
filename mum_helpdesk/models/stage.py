from odoo import _, api, fields, models, Command


class TicketStage(models.Model):
    _inherit = 'helpdesk.ticket.stage'

    readonly = fields.Boolean(string='Readonly Form')