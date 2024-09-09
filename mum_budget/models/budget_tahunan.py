from odoo import _, api, fields, models, Command


class BudgetTahunan(models.Model):
    _name = 'anggaran.tahunan'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _description = 'Anggaran Tahunan'

    name = fields.Char(string='Anggaran')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda s:s.env.company.id)
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', default=lambda s:s.env.company.currency_id.id)
    total_anggaran = fields.Float(string='Total Anggaran')
    total_pengajuan_anggaran = fields.Float(string='Total Pengajuan')
    total_realisasi_anggaran = fields.Float(string='Total Realisasi')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('done', 'Done'),
    ], string='State', default='draft', copy=False, tracking=1)
    # anggaran_bulanan_ids = fields.One2many(comodel_name='anggaran.bulanan', inverse_name='anggaran_tahunan_id', string='Anggaran Bulanan')
    # anggaran_bulanan_divisi_ids = fields.One2many(comodel_name='anggaran.bulanan.divisi', inverse_name='anggaran_tahunan_id', string='Anggaran Bulanan Divisi')




    #CRUD METHOD
    @api.model
    def create(self,vals):
        return super().create(vals)

    def write(self,vals):
        return super().write(vals)

    def unlink(self):
        return super().unlink()



    #LOGIC METHOD



    #BUTTON METHOD
    def button_submit(self):
        return self.write({'state' : 'submit'})
    
    def button_done(self):
        return self.write({'state' : 'done'})
    
    def button_reopen(self):
        return self.write({'state' : 'draft'})


    #ACTION METHOD
