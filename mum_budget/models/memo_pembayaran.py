from odoo import _, api, fields, models, Command


class MemoPembayaran(models.Model):
    _name = 'memo.pembayaran'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _description = 'Memo Pembayaran'

    name = fields.Char(string='Nomor')
    tanggal = fields.Date(string='Tanggal')
    to_employee_id = fields.Many2one(comodel_name='hr.employee', string='Kepada')
    from_employee_id = fields.Many2one(comodel_name='hr.employee', string='Dari')
    perihal = fields.Char(string='Perihal')
    keterangan = fields.Char('Keterangan')
    journal_id = fields.Many2one(comodel_name='account.journal', string='Pengeluaran', domain=[('type', '=', 'bank')])
    tgl_saldo = fields.Date(string='Tanggal Saldo')
    saldo_bank = fields.Monetary('Saldo Bank')
    total_pembayaran = fields.Monetary('Total Bayar', compute='_compute_total_pembayaran')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', related='journal_id.currency_id')
    invoice_ids = fields.Many2many(comodel_name='account.move', string='Invoices')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda s:s.env.company.id)
    trops_employee_id = fields.Many2one(comodel_name='hr.employee', string='Trops Sign')
    anggaran_employee_id = fields.Many2one(comodel_name='hr.employee', string='Anggaran Sign')
    kabag_employee_id = fields.Many2one(comodel_name='hr.employee', string='Kabag Sign')
    kadiv_employee_id = fields.Many2one(comodel_name='hr.employee', string='Kadiv Sign')
    dirut_employee_id = fields.Many2one(comodel_name='hr.employee', string='Dirut Sign')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('trops', 'Trops'),
        ('anggaran', 'Anggaran'),
        ('kabag', 'Kabag'),
        ('kadiv', 'Kadiv'),
        ('dirut', 'Dirut'),
        ('waiting', 'Waiting Payment'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft', copy=False, tracking=1)
    melebihi_limit = fields.Boolean('Melebihi Limit', compute='_compute_melebihi_limit')



    #CRUD METHOD
    @api.model
    def create(self,vals):
        name = self.env['ir.sequence'].next_by_code('memo.pembayaran.seq') or ''
        vals['name'] = 'M-' + name
        return super().create(vals)

    def write(self,vals):
        return super().write(vals)

    def unlink(self):
        return super().unlink()



    #LOGIC METHOD
    @api.depends('invoice_ids')
    def _compute_melebihi_limit(self):
        # params = self.env['ir.config_parameter'].sudo()
        params = self.env['ir.config_parameter'].sudo().get_param('mum_budget.default_limit_memo_pembayaran')
        for rec in self:
            rec.melebihi_limit = any(x.amount_total >= float(params) for x in rec.invoice_ids)

    @api.depends('invoice_ids')
    def _compute_total_pembayaran(self):
        for rec in self:
            rec.total_pembayaran = sum(x.amount_total for x in rec.invoice_ids)



    #BUTTON METHOD
    def button_submit(self):
        return self.write({'state' : 'trops'})

    def button_to_anggaran(self):
        return self.write({'state' : 'anggaran', 'trops_employee_id' : self.env.user.employee_id.id})

    def button_to_kabag(self):
        return self.write({'state' : 'kabag', 'anggaran_employee_id' : self.env.user.employee_id.id})

    def button_to_kadiv(self):
        return self.write({'state' : 'kadiv', 'kabag_employee_id' : self.env.user.employee_id.id})

    def button_to_dirut(self):
        return self.write({'state' : 'dirut', 'kadiv_employee_id' : self.env.user.employee_id.id})

    def button_waiting(self):
        employee_id = self.env.user.employee_id.id
        vals = {'state' : 'waiting'}
        if self.melebihi_limit:
            vals.update({
                'dirut_employee_id' : employee_id
            })
        else:
            vals.update({
                'kadiv_employee_id' : employee_id
            })
        return self.write(vals)
    
    def button_done(self):
        employee_id = self.env.user.employee_id.id
        vals = {'state' : 'done'}
        self.write(vals)
        return self.invoice_ids.action_register_payment()
    
    def button_draft(self):
        return self.write({'state' : 'draft'})
    
    def button_cancel(self):
        return self.write({'state' : 'cancel'})




    #ACTION METHOD
    def open_register_payment(self):
        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.invoice_ids.ids,
                'memo_pembayaran_id' : self.id
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
