from odoo import _, api, fields, models, Command


class PengajuanAnggaran(models.Model):
    _name = 'pengajuan.anggaran'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _description = 'Pengajuan Anggaran'

    name = fields.Char(string='Name')
    anggaran_divisi_id = fields.Many2one(comodel_name='anggaran.bulanan.divisi', string='Anggaran Divisi')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan', default=lambda s:s.env.user.employee_id)
    product_id = fields.Many2one(comodel_name='product.product', string='Item Pengajuan')
    tanggal_pengajuan = fields.Date(string='Tanggal Pengajuan', default=lambda s:fields.Date.context_today(s))
    tanggal_pertanggungjawaban = fields.Date(string='Tanggal Pertanggungjawaban')
    bagian_id = fields.Many2one(comodel_name='hr.department', string='Bagian')
    divisi_id = fields.Many2one(comodel_name='hr.department', string='Divisi', related='bagian_id.divisi_id')
    tax_ids = fields.Many2many(comodel_name='account.tax', string='Pajak')
    nilai_pengajuan = fields.Float(string='Nilai Pengajuan')
    nilai_realisasi = fields.Float(string='Nilai Realisasi')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Diajukan'),
        ('approval', 'Approval'),
        ('realisasi', 'Pertanggungjawaban'),
        ('done', 'Closed'),
        ('cancel', 'Cancel'),], default='draft', copy=False, string="Status", tracking=1)




    #CRUD METHOD
    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('pengajuan.anggaran.seq')
        return super().create(vals)

    def write(self,vals):
        return super().write(vals)

    def unlink(self):
        return super().unlink()



    #BUTTON METHOD



    #ACTION METHOD



    #LOGIC METHOD
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.bagian_id = self.employee_id and self.employee_id.department_id.id or False
