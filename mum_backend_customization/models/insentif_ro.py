from odoo import _, api, fields, models, Command


class InsentifRo(models.Model):
	_name = 'insentif.ro'
	_inherit = ['mail.activity.mixin', 'mail.thread']
	_description = 'Insentif RO'
	_check_company_auto = True

	name = fields.Char(string='Name')
	tgl_dibuat = fields.Date(string='Tanggal Dibuat')
	periode_id = fields.Many2one(comodel_name='insentif.periode', string='Periode Insentif')
	month_ids = fields.Many2many(comodel_name='res.month', string='Bulan')
	kro_id = fields.Many2one(comodel_name='hr.employee', string='KRO')
	state = fields.Selection(string='State', selection=[
		('draft', 'Draft'), 
		('in_progress', 'In Progress'),
		('submit', 'Submit'),
		('done', 'Done')], default='draft', copy=False, tracking=True)
	company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda self:self.env.company)
	insentif_ro_employee_ids = fields.One2many(comodel_name='insentif.ro.employee', inverse_name='insentif_ro_id', string='Insenfif RO Employee')
	insentif_ro_employee_line_ids = fields.One2many(comodel_name='insentif.ro.employee.line', inverse_name='insentif_ro_id', string='Insentif RO Employee Line')

	@api.model
	def create(self, values):
		# CODE HERE
		vals['name'] = self.env['ir.sequence'].next_by_code('kpi.insentif.ro.seq', fields.Date.to_date(vals.get('tgl_dibuat')))
		return super(InsentifRo, self).create(values)
	
	# def button_confirm(self):



class InsentifRoLine(models.Model):
	_name = 'insentif.ro.employee'
	_description = 'Insentif RO Employee Line'
	_rec_name = 'employee_id'

	# name = fields.Char(string='Name')
	insentif_ro_id = fields.Many2one(comodel_name='insentif.ro', string='Insentif RO')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='Karyawan')
	total_resign = fields.Integer(string='Total Resign')
	total_rekrutmen = fields.Integer(string='Total Rekrutmen')
	total_tl = fields.Integer(string='Total TL')
	company_id = fields.Many2one(comodel_name='res.company', string='Company', related='insentif_ro_id.company_id', store=True, precompute=True)
	insentif_ro_employee_line_ids = fields.One2many(comodel_name='insentif.ro.employee.line', inverse_name='insentif_ro_employee_id', string='Insentif RO Employee Line')
	
	def action_show_details(self):
		self.ensure_one()
		view = self.env.ref('mum_backend_customization.insentif_ro_employee_view_form')
		return {
			'name': _('Detail KPI Karyawan %s'%self.employee_id.name),
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': self._name,
			'views': [(view.id, 'form')],
			'view_id': view.id,
			'target': 'new',
			'res_id': self.id,
		}

class InsentifRoEmployeeLine(models.Model):
	_name = 'insentif.ro.employee.line'
	_description = 'Insentif RO Employee Line'


	insentif_ro_id = fields.Many2one(comodel_name='insentif.ro', string='Insentif RO')
	insentif_ro_employee_id = fields.Many2one(comodel_name='insentif.ro.employee', string='Insentif RO Employee')
	name = fields.Char(string='Name')
	month_id = fields.Many2one(comodel_name='res.month', string='Bulan')
	cabang = fields.Integer(string='Cabang')
	formasi = fields.Integer(string='Formasi')
	aktif = fields.Integer(string='Aktif')
	resign = fields.Integer(string='Resign')
	rekrutmen = fields.Integer(string='Rekrutmen')
	tl = fields.Integer(string='TL')
	pencapaian_rekrutmen = fields.Float(string='Pencapaian Rekrutmen')
	pencapaian_maintain = fields.Float(string='Pencapaian Maintain')
	pencapaian_tl = fields.Float(string='Pencapaian TL')
	grade_rekrutmen = fields.Char(string='Grade Rekrutmen')
	grade_maintain = fields.Char(string='Grade Maintain')
	grade_tl = fields.Char(string='Grade TL')
	average = fields.Float(string='Average')
	grade_average = fields.Char(string='Grade Average')
	wilayah_suffer_id = fields.Many2one(comodel_name='wilayah.suffer', string='Wilayah Suffer')
	company_id = fields.Many2one(comodel_name='res.company', string='Company', related='insentif_ro_id.company_id', store=True, precompute=True)




