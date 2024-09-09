from odoo import _, api, fields, models, Command


class JobTitle(models.Model):
    _inherit = 'job.title'

    uang_saku_spd = fields.Float(string='Uang Saku SPD')
    uang_penginapan_spd = fields.Float(string='Uang Penginapan SPD')
    # transportasi_lokal =
