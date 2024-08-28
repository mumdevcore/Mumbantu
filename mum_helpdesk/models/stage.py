from odoo import _, api, fields, models, Command


class TicketStage(models.Model):
    _inherit = 'helpdesk.ticket.stage'

    readonly = fields.Boolean(string='Readonly Form')
    sequence = fields.Integer(index=True)

    """
        staging sequence:
        baru                    = 1
        sedang diproses         = 2
        menunggu konfirmasi     = 3
        selsai                  = 100
        revisi                  = 200
        reject                  = 999
    """