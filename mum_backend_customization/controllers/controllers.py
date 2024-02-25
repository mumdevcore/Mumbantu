# -*- coding: utf-8 -*-
# from odoo import http


# class MumHrSkills(http.Controller):
#     @http.route('/mum_hr_skills/mum_hr_skills', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mum_hr_skills/mum_hr_skills/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mum_hr_skills.listing', {
#             'root': '/mum_hr_skills/mum_hr_skills',
#             'objects': http.request.env['mum_hr_skills.mum_hr_skills'].search([]),
#         })

#     @http.route('/mum_hr_skills/mum_hr_skills/objects/<model("mum_hr_skills.mum_hr_skills"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mum_hr_skills.object', {
#             'object': obj
#         })
