# Copyright 2023 Artem Shurshilov
# Odoo Proprietary License v1.0


from odoo import fields, models


class AttachmentHistory(models.Model):
    _name = "ir.attachment.history"
    _description = "Attachment changed history"

    name = fields.Char(string="Name")
    number = fields.Char(string="Number")
    user_id = fields.Many2one("res.users", string="User")
    attachment = fields.Binary(string="Version attachment")
    # attachment = fields.Binary(string="Version attachment",attachment=False, store=True, readonly=True,)
    vals = fields.Text(string="Vals changed")
    attachment_id = fields.Many2one(
        "ir.attachment", string="Related attachment"
    )
