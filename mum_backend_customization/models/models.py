# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class mum_hr_skills(models.Model):
#     _name = 'mum_hr_skills.mum_hr_skills'
#     _description = 'mum_hr_skills.mum_hr_skills'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
