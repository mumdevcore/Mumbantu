# -*- coding: utf-8 -*-
# from odoo import http


# class MumKpi(http.Controller):
#     @http.route('/mum_kpi/mum_kpi', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mum_kpi/mum_kpi/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mum_kpi.listing', {
#             'root': '/mum_kpi/mum_kpi',
#             'objects': http.request.env['mum_kpi.mum_kpi'].search([]),
#         })

#     @http.route('/mum_kpi/mum_kpi/objects/<model("mum_kpi.mum_kpi"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mum_kpi.object', {
#             'object': obj
#         })
