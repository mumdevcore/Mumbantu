# -*- coding: utf-8 -*-
# from odoo import http


# class MumDms(http.Controller):
#     @http.route('/mum_dms/mum_dms', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mum_dms/mum_dms/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mum_dms.listing', {
#             'root': '/mum_dms/mum_dms',
#             'objects': http.request.env['mum_dms.mum_dms'].search([]),
#         })

#     @http.route('/mum_dms/mum_dms/objects/<model("mum_dms.mum_dms"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mum_dms.object', {
#             'object': obj
#         })
