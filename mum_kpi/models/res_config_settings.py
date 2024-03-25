from odoo import _, api, fields, models, Command


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'New Description'

    position_default_job_ro_id = fields.Many2one(comodel_name='hr.job', string='Job Position RO', config_parameter='mum_kpi.default_job_ro_id',)
    position_default_job_alw_id = fields.Many2one(comodel_name='hr.job', string='Job Position ALW', config_parameter='mum_kpi.default_job_alw_id',)
