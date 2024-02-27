# Copyright 2020-2023 Artem Shurshilov
# Odoo Proprietary License v1.0


from odoo import api, fields, models


class IrAttachmentTag(models.Model):
    _name = "ir.attachment.tag"
    _description = "Attachment Tag"
    _parent_store = True

    name = fields.Char("Tag Name", required=True, translate=True)
    active = fields.Boolean(
        help="The active field allows you to hide the tag without removing it.",
        default=True,
    )
    parent_id = fields.Many2one(
        string="Parent Tag",
        comodel_name="ir.attachment.tag",
        index=True,
        ondelete="cascade",
    )
    child_id = fields.One2many(
        string="Child Tags",
        comodel_name="ir.attachment.tag",
        inverse_name="parent_id",
    )
    parent_path = fields.Char(index=True)
    image = fields.Binary("Image")

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Tag name already exists!"),
    ]

    # @api.multi
    def name_get(self):
        """Return the tags' display name, including their direct parent."""
        res = {}
        for record in self:
            current = record
            name = current.name
            while current.parent_id:
                name = "%s / %s" % (current.parent_id.name, name)
                current = current.parent_id
            res[record.id] = name

        return [(record.id, res[record.id]) for record in self]

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(" / ")[-1]
            args = [("name", operator, name)] + args
        tags = self.search(args, limit=limit)
        return tags.name_get()
