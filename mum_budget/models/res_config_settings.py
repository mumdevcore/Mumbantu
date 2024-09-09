from odoo import _, api, fields, models, Command


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    item_uang_saku_spd_id = fields.Many2one(comodel_name='product.product', string='Item Uang Saku', config_parameter="mum_budget.default_item_uang_saku_spd_id")
    item_penginapan_spd_id = fields.Many2one(comodel_name='product.product', string='Item Penginapan', config_parameter="mum_budget.default_item_penginapan_spd_id")
    item_transportasi_lokal_spd_id = fields.Many2one(comodel_name='product.product', string='Item Transportasi Lokal', config_parameter="mum_budget.default_item_transportasi_lokal_spd_id")
    item_trans_utama_berangkat_spd_id = fields.Many2one(comodel_name='product.product', string='Item Transportasi Utama Berangkat', config_parameter="mum_budget.default_item_trans_utama_berangkat_spd_id")
    item_trans_utama_kembali_spd_id = fields.Many2one(comodel_name='product.product', string='Item Transportasi Utama Kembali', config_parameter="mum_budget.default_item_trans_utama_kembali_spd_id")
    item_airport_tax_spd_id = fields.Many2one(comodel_name='product.product', string='Item Airport Tax', config_parameter="mum_budget.default_item_airport_tax_spd_id")
    item_fiskal_spd_id = fields.Many2one(comodel_name='product.product', string='Item Fiskal', config_parameter="mum_budget.default_item_fiskal_spd_id")
    item_penjamuan_spd_id = fields.Many2one(comodel_name='product.product', string='Item Biaya Penjamuan', config_parameter="mum_budget.default_item_penjamuan_spd_id")
    item_lainnya_spd_id = fields.Many2one(comodel_name='product.product', string='Item Biaya Lainnya', config_parameter="mum_budget.default_item_lainnya_spd_id")
    limit_memo_pembayaran = fields.Float(string="Limit Memo Pembayaran", config_parameter='mum_budget.default_limit_memo_pembayaran')
