from odoo import _, api, fields, models, Command


class HelpdeskTicketTeam(models.Model):
	_inherit = 'helpdesk.ticket.team'

	stage_ids = fields.Many2many(comodel_name='helpdesk.ticket.stage', string='Stages', compute='_compute_stage_ids')
	new_ticket_count = fields.Integer(compute='_compute_outstanding_ticket')
	in_progress_ticket_count = fields.Integer(compute='_compute_outstanding_ticket')
	waiting_ticket_count = fields.Integer(compute='_compute_outstanding_ticket')
	revision_ticket_count = fields.Integer(compute='_compute_outstanding_ticket')


	#CRUD METHOD
	@api.model
	def create(self,vals):
		return super().create(vals)

	def write(self,vals):
		return super().write(vals)

	def unlink(self):
		return super().unlink()



	#LOGIC METHOD
	@api.depends('ticket_ids')
	def _compute_stage_ids(self):
		for rec in self:
			rec.stage_ids = rec.env['helpdesk.ticket.stage'].search([])

	@api.depends("ticket_ids", 'ticket_ids.stage_id')
	def _compute_outstanding_ticket(self):
		
		ticket_model = self.env["helpdesk.ticket"]
		stage_ids = self.env['helpdesk.ticket.stage'].search([('sequence', 'in', (1,2,3,200))])
		fetch_data = ticket_model.read_group(
			[('team_id', 'in', self.ids),("stage_id", "in", stage_ids.ids)],
			["team_id", "stage_id"],
			["team_id", "stage_id"],
			lazy=False,
		)
		result = [
			[
				data["team_id"][0],
				data["stage_id"] and data["stage_id"][0],
				data["__count"],
			]
			for data in fetch_data
		]
		for team in self:
			team.new_ticket_count = sum(r[2] for r in result if r[0] == team.id and r[1] in stage_ids.filtered(lambda s:s.sequence == 1).ids)
			team.in_progress_ticket_count = sum(r[2] for r in result if r[0] == team.id and r[1] in stage_ids.filtered(lambda s:s.sequence == 2).ids)
			team.waiting_ticket_count = sum(r[2] for r in result if r[0] == team.id and r[1] in stage_ids.filtered(lambda s:s.sequence == 3).ids)
			team.revision_ticket_count = sum(r[2] for r in result if r[0] == team.id and r[1] in stage_ids.filtered(lambda s:s.sequence == 200).ids)
	
	#BUTTON METHOD
	



	#ACTION METHOD
	def action_button_new(self):
		self.ensure_one()
		view = self.env.ref('helpdesk_mgmt.ticket_view_tree')
		form = self.env.ref('helpdesk_mgmt.ticket_view_form')
		ticket_ids = self.ticket_ids.filtered(lambda s:s.stage_id.sequence == 1)
		
		return {
			'name': _('Tiket Baru %s'%self.name),
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'res_model': 'helpdesk.ticket',
			'views': [(view.id, 'tree'), (form.id, 'form')],
			'view_id': view.id,
			'target': 'self',
			'domain' : [('id', 'in', ticket_ids.ids)]
		}

	def action_button_in_progress(self):
		self.ensure_one()
		view = self.env.ref('helpdesk_mgmt.ticket_view_tree')
		form = self.env.ref('helpdesk_mgmt.ticket_view_form')
		ticket_ids = self.ticket_ids.filtered(lambda s:s.stage_id.sequence == 2)
		
		return {
			'name': _('Tiket Diproses %s'%self.name),
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'res_model': 'helpdesk.ticket',
			'views': [(view.id, 'tree'), (form.id, 'form')],
			'view_id': view.id,
			'target': 'self',
			'domain' : [('id', 'in', ticket_ids.ids)]
		}

	def action_button_waiting(self):
		self.ensure_one()
		view = self.env.ref('helpdesk_mgmt.ticket_view_tree')
		form = self.env.ref('helpdesk_mgmt.ticket_view_form')
		ticket_ids = self.ticket_ids.filtered(lambda s:s.stage_id.sequence == 3)
		
		return {
			'name': _('Tiket Menunggu Konfirmasi %s'%self.name),
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'res_model': 'helpdesk.ticket',
			'views': [(view.id, 'tree'), (form.id, 'form')],
			'view_id': view.id,
			'target': 'self',
			'domain' : [('id', 'in', ticket_ids.ids)]
		}

	def action_button_revision(self):
		self.ensure_one()
		view = self.env.ref('helpdesk_mgmt.ticket_view_tree')
		form = self.env.ref('helpdesk_mgmt.ticket_view_form')
		ticket_ids = self.ticket_ids.filtered(lambda s:s.stage_id.sequence == 200)
		
		return {
			'name': _('Tiket Revisi %s'%self.name),
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'res_model': 'helpdesk.ticket',
			'views': [(view.id, 'tree'), (form.id, 'form')],
			'view_id': view.id,
			'target': 'self',
			'domain' : [('id', 'in', ticket_ids.ids)]
		}

	
