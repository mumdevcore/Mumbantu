from odoo import _, api, fields, models, Command


class TemplateLampiranInvoice(models.Model):
    _name = 'template.lampiran.invoice'
    _description = 'Template Dokumen Pendukung Tagihan'

    sequence = fields.Integer()
    name = fields.Char(string='Label')


class LampiranInvoice(models.Model):
    _name = 'lampiran.invoice'
    _description = 'Lampiran Invoice'
    _order = 'sequence'

    sequence = fields.Integer(string='Sequence')
    move_id = fields.Many2one(comodel_name='account.move', string='Account Move')
    checklist = fields.Boolean('Checklist')
    name = fields.Char(string='Name')
    description = fields.Char(string='Description')