# Copyright 2020-2023 Artem Shurshilov
# Odoo Proprietary License v1.0

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    tag_ids = fields.Many2many(
        string="Tags",
        comodel_name="ir.attachment.tag",
        relation="ir_attachment_tag_rel",
        column1="tag_id",
        column2="attachment_id",
    )
    history_ids = fields.One2many(
        comodel_name="ir.attachment.history",
        inverse_name="attachment_id",
        string="History attachment",
    )
    category_id = fields.Many2one(
        comodel_name="ir.attachment.category",
        string="Category",
    )
    number = fields.Char("Number", readonly=True)
    active = fields.Boolean(
        "Active",
        default=True,
        help="If unchecked, it will allow you to hide the attachment without removing it.",
    )

    def _read_group_allowed_fields(self):
        return [
            "type",
            "company_id",
            "res_id",
            "create_date",
            "create_uid",
            "name",
            "mimetype",
            "id",
            "url",
            "res_field",
            "res_model",
            "tag_ids",
            "category_id",
        ]

    def _check_groups_access(self, groups_ids):
        if not groups_ids or groups_ids & self.env.user.groups_id:
            return
        # for group in groups_ids:
        #     external_id = group.get_external_id()[group.id]
        #     if self.env.user.has_group(str(external_id)) or self.env.user._is_admin() or self.env.su:
        #         return
        # # TODO: do or not?
        # if not len(groups_ids):
        #     return
        raise ValidationError(
            """Your user's access groups are not included in the list of allowed \n
                    access groups for these attachments, contact your administrator"""
        )

    @api.model
    def search(self, *args, **kwargs):
        res = super().search(*args, **kwargs)
        res2 = self.env["ir.attachment"]
        if type(res) == type(res2):
            for rec in res:
                if rec.category_id and rec.category_id.read_check:
                    if (
                        not rec.category_id.group_ids
                        or rec.category_id.group_ids & self.env.user.groups_id
                    ):
                        continue
                    else:
                        res2 += rec
            return res - res2
        return res

    @api.model_create_multi
    def create(self, vals):
        attachments = super().create(vals)
        for res in attachments:
            category_id = None
            if res.category_id:
                category_id = res.category_id
            else:
                # find category by model
                if res.res_model:
                    category_id = (
                        res.env["ir.attachment.category"]
                        .sudo()
                        .search([("model_id", "=", res.res_model)], limit=1)
                    )
                    res.category_id = category_id.id

            if category_id:
                # CHECK ACCESS
                if category_id.create_check:
                    self._check_groups_access(category_id.group_ids)

                # NUMBERING
                if (
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("attachments_history_and_numbering")
                ):
                    res.number = self.env["ir.sequence"].next_by_code(
                        "advance_contract.contract"
                    )
        return attachments

    def unlink(self):
        for i in self:
            # CHECK ACCESS
            if i.category_id and i.category_id.delete_check:
                i._check_groups_access(i.category_id.group_ids)
        return super().unlink()

    def write(self, vals):
        for item in self:
            category_id = None
            if item.category_id:
                category_id = item.category_id
            else:
                # find category by model
                if item.res_model:
                    category_id = (
                        item.env["ir.attachment.category"]
                        .sudo()
                        .search([("model_id", "=", item.res_model)], limit=1)
                    )
                    vals["category_id"] = category_id.id

            if category_id:
                # CHECK ACCESS
                if category_id.write_check:
                    item._check_groups_access(category_id.group_ids)

                if (
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("attachments_history_and_numbering")
                ):
                    # NUMBERING
                    vals["number"] = item.env["ir.sequence"].next_by_code(
                        "advance_contract.contract"
                    )
                    # HISTORY
                    data = {
                        # old number and name
                        "name": item.name,
                        "number": item.number,
                        "user_id": self.env.user.id,
                        "attachment_id": item.id,
                    }
                    # if binary data changed
                    if "datas" in vals:
                        data.update({"attachment": item.datas})
                    else:
                        data.update({"vals": vals})
                    self.env["ir.attachment.history"].sudo().create(data)

        return super().write(vals)

    def download_filter(self):
        return {
            "type": "ir.actions.act_url",
            "url": "/web/binary/download_document_ids?ids="
            + str(self.ids).replace(" ", ""),
        }
