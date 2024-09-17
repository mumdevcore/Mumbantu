from odoo import _, api, fields, models, Command


class FormulirPermintaanPembayaran(models.Model):
    _name = 'formulir.permintaan.pembayaran'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _description = 'Permintaan Pembayaran'

    name = fields.Char(string='Nomor')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan')
    job_id = fields.Many2one(comodel_name='hr.job', string='Posisi')
    bagian_id = fields.Many2one(comodel_name='hr.department', string='Bagian')
    nominal = fields.Monetary(string="Nominal")
    product_id = fields.Many2one(comodel_name='product.product', string='Item/Product',)
    perihal = fields.Char(string='Perihal')
    date = fields.Date(string='Tanggal')
    user_can_approve = fields.Boolean(compute='_compute_user_can_approve')
    empl_approval1_id = fields.Many2one(comodel_name='hr.employee', string='Employee Approval 1')
    approval1_date = fields.Date(string='Tgl Approval 1')
    empl_approval2_id = fields.Many2one(comodel_name='hr.employee', string='Employee Approval 2')
    approval2_date = fields.Date(string='Tgl Approval 2')
    empl_approval3_id = fields.Many2one(comodel_name='hr.employee', string='Employee Aprroval 3')
    approval3_date = fields.Date(string='Tgl Approval 2')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', default=lambda s:s.env.company.currency_id.id)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submited'),
        ('approval_1', 'Approval 1'),
        ('approval_2', 'Approval 2'),
        ('approval_3', 'Approval 3'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string="State", tracking=True, copy=False, default='draft')



    #CRUD METHOD
    @api.model
    def create(self,vals):
        return super().create(vals)

    def write(self,vals):
        return super().write(vals)

    def unlink(self):
        return super().unlink()



    #LOGIC METHOD
    def _compute_user_can_approve(self):
        for rec in self:
            rec.user_can_approve = True



    #BUTTON METHOD



    #ACTION METHOD
