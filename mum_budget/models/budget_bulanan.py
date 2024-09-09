from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError

class AnggaranBulanan(models.Model):
    _name = 'anggaran.divisi'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _description = 'Anggaran Bulanan'

    name = fields.Char(string='Anggaran Bulanan')
    crossovered_budget_id = fields.Many2one(comodel_name='crossovered.budget', string='Anggaran Tahunan')
    month_id = fields.Many2one(comodel_name='res.month', string='Bulan')
    tahun = fields.Char(string='Tahun')
    divisi_id = fields.Many2one(comodel_name='hr.department', string='Divisi', domain=[('divisi', '=', True)])
    company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda s:s.env.company.id)
    budget_divisi_ids = fields.One2many(comodel_name='anggaran.bulanan.divisi', inverse_name='budget_bulanan_id', string='Anggaran Bulanan Divisi')
    planned_amount = fields.Monetary('Nilai Anggaran')
    practical_amount = fields.Monetary('Realisasi Anggaran')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', related='company_id.currency_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('done', 'Closed'),], string='Status', default='draft', copy=False, compute='_compute_state', store=True, precompute=True)
    
    # Constrains Method
    @api.constrains('name')
    def _check_unique_name(self):
        for rec in self:
            domain = [('divisi_id', '=', rec.divisi_id.id), ('tahun', '=', rec.tahun), ('id', '!=', rec.id)]
            if rec.search(domain):
                raise ValidationError(_(f"Anggaran untuk {rec.name} sudah ada."))

    # CRUD Method
    @api.model
    def create(self, vals):
        divisi_id = self.env['hr.department'].browse(vals.get('divisi_id'))
        vals['name'] = f"{divisi_id.name}-{vals.get('tahun')}"
        return super().create(vals)


    # Logic and Compute Method
    @api.depends('budget_divisi_ids.state')
    def _compute_state(self):
        for rec in self:
            if all(line.state == 'done' for line in rec.budget_divisi_ids):
                rec.state = 'done'
            elif all(line.state == 'open' for line in rec.budget_divisi_ids):
                rec.state = 'open'
            else:
                rec.state = 'draft'
            

    # Button Method
    def button_open(self):
        if not self.budget_divisi_ids:
            raise ValidationError(_("Anggaran tidak dapat dibuka, dikarenakan belum ada alokasi anggaran ke divisi."))
        self.budget_divisi_ids.write({'state' : 'open'})
    
    def button_close(self):
        self.budget_divisi_ids.write({'state' : 'done'})
    
    def button_reopen(self):
        self.budget_divisi_ids.write({'state' : 'draft'})
    
    # Action Method
    

class AnggaranBulananDivisi(models.Model):
    _name = 'anggaran.bulanan.divisi'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _description = 'Anggaran Bulanan Divisi'

    name = fields.Char(string='Anggaran Bulanan')
    crossovered_budget_id = fields.Many2one(comodel_name='crossovered.budget', string='Anggaran Tahunan')
    budget_bulanan_id = fields.Many2one(comodel_name='anggaran.divisi', string='Anggaran Bulanan')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', related='budget_bulanan_id.company_id')
    divisi_id = fields.Many2one(comodel_name='hr.department', string='Divisi')
    month_id = fields.Many2one(comodel_name='res.month', string='Bulan')
    tahun = fields.Char(string='Tahun', related='budget_bulanan_id.tahun', store=True)

    # Field detail anggaran
    total_anggaran = fields.Monetary(string='Total Anggaran')
    pengajuan_anggaran = fields.Monetary(string='Total Pengajuan', compute='_compute_pengajuan_realisasi')
    realisasi_anggaran = fields.Monetary(string='Realisasi Anggaran', compute='_compute_pengajuan_realisasi')
    sisa_anggaran = fields.Monetary(string='Sisa Anggaran', compute='_compute_pengajuan_realisasi')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', default=lambda s:s.env.company.currency_id.id)
    pengajuan_anggaran_ids = fields.One2many(comodel_name='pengajuan.anggaran', inverse_name='anggaran_divisi_id', string='Pengajuan Anggaran')


    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('done', 'Closed'),], string='Status', default='draft', copy=False,)


    @api.constrains('name')
    def _check_unique_name(self):
        for rec in self:
            domain = [('month_id', '=', rec.month_id.id), ('tahun', '=', rec.tahun), ('id', '!=', rec.id)]
            if rec.search(domain):
                raise ValidationError(_(f"Anggaran untuk {rec.name} sudah ada."))

    # CRUD Method
    @api.model
    def create(self, vals):
        month_id = self.env['res.month'].browse(vals.get('month_id'))
        vals['name'] = f"{month_id.name}-{vals.get('tahun')}"
        return super().create(vals)
    # @api.model
    # def create(self,vals):
    #     vals['name'] = self.env['ir.sequence'].next_by_code('anggaran.divisi.bulanan.seq')
        
    #     return super().create(vals)

    def write(self,vals):
        return super().write(vals)

    def unlink(self):
        return super().unlink()
    
    #LOGIC METHOD
    def _compute_pengajuan_realisasi(self):
        for rec in self:
            rec.pengajuan_anggaran = sum(line.nilai_pengajuan for line in rec.pengajuan_anggaran_ids.filtered(lambda l:l.state not in ('cancel')))
            rec.realisasi_anggaran = sum(line.nilai_realisasi for line in rec.pengajuan_anggaran_ids.filtered(lambda l:l.state not in ('cancel')))
            rec.sisa_anggaran = rec.total_anggaran - rec.realisasi_anggaran

    #BUTTON METHOD
    def button_open(self):
        self.write({'state' : 'open'})
    
    def button_close(self):
        self.write({'state' : 'done'})
    
    def button_reopen(self):
        self.write({'state' : 'draft'})


    #ACTION METHOD



   
