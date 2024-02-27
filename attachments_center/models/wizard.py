# Copyright 2021-2023 Artem Shurshilov
# Odoo Proprietary License v1.0

# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, or if you have received a written
# agreement from the authors of the Software (see the COPYRIGHT file).

# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).

# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.

# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class IrAttachmentWizard(models.Model):
    _name = "ir.attachment.wizard"
    _description = "Attachment Center Wizard Setup"

    # category_ids = fields.Many2many(
    #     comodel_name="ir.attachment.category",
    #     string="Category",
    # )

    count_directories = fields.Char(
        compute="_compute_count_directories", string="Found directories"
    )
    attachments_in_directory = fields.Char(
        compute="_compute_attachments_in_directory",
        string="Attachments in directory",
    )

    def create_categories(self):
        # exclude system files
        model_ids = (
            self.env["ir.model"]
            .sudo()
            .search(
                [
                    ("model", "!=", "ir.ui.view"),
                    ("model", "!=", False),
                    ("model", "!=", "ir.module.module"),
                ]
            )
        )
        self.env["bus.bus"]._sendone(
            self.env.user.partner_id,
            "mail.simple_notification",
            {
                "title": _("Find %s models" % len(model_ids)),
                "message": _("If you wanna check it go to directories menu"),
            },
        )
        for model in model_ids:
            exist = (
                self.env["ir.attachment.category"]
                .sudo()
                .search([("name", "=", model.name)])
            )
            if not exist:
                self.env["ir.attachment.category"].create(
                    {
                        "name": model.name,
                        "model_id": model.id,
                    }
                )

    def _compute_count_directories(self):
        category_all = (
            self.env["ir.attachment.category"].sudo().search_count([])
        )
        self.count_directories = "%s" % category_all

    def _compute_attachments_in_directory(self):
        attachments_all = self.env["ir.attachment"].sudo().search_count([])
        attachments_linked = (
            self.env["ir.attachment"]
            .sudo()
            .search_count([("category_id", "!=", False)])
        )
        self.attachments_in_directory = "All / in directories (%s / %s)" % (
            attachments_all,
            attachments_linked,
        )

    def delete_empty_categories(self):
        category_ids = self.env["ir.attachment.category"].sudo().search([])
        if not len(category_ids):
            raise ValidationError(
                "No categories / directories, please add them first"
            )
        for rec in category_ids:
            if not rec.count_total_files and not rec.count_files:
                rec.unlink()

    def link_attachments_model(self):
        category_ids = self.env["ir.attachment.category"].sudo().search([])
        if not len(category_ids):
            raise ValidationError(
                "No categories / directories, please add them first"
            )

        models = [categ.model_id.model for categ in category_ids]

        attachments_ids = (
            self.env["ir.attachment"]
            .sudo()
            .search([("category_id", "=", False), ("res_model", "in", models)])
        )
        self.env["bus.bus"]._sendone(
            self.env.user.partner_id,
            "mail.simple_notification",
            {
                "title": _("Find %s attachments" % len(attachments_ids)),
                "message": _("Start linked proccess"),
            },
        )
        for record in attachments_ids:
            record.name = record.name
        self.env["bus.bus"]._sendone(
            self.env.user.partner_id,
            "mail.simple_notification",
            {
                "title": _("Success"),
                "message": _("Link proccess completed success"),
            },
        )
