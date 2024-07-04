# -*- coding: utf-8 -*-
# from odoo import http


# class MumReport(http.Controller):
#     @http.route('/mum_report/mum_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mum_report/mum_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mum_report.listing', {
#             'root': '/mum_report/mum_report',
#             'objects': http.request.env['mum_report.mum_report'].search([]),
#         })

#     @http.route('/mum_report/mum_report/objects/<model("mum_report.mum_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mum_report.object', {
#             'object': obj
#         })
