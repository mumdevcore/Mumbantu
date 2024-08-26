# -*- coding: utf-8 -*-
# from odoo import http


# class MumHelpdesk(http.Controller):
#     @http.route('/mum_helpdesk/mum_helpdesk', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mum_helpdesk/mum_helpdesk/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mum_helpdesk.listing', {
#             'root': '/mum_helpdesk/mum_helpdesk',
#             'objects': http.request.env['mum_helpdesk.mum_helpdesk'].search([]),
#         })

#     @http.route('/mum_helpdesk/mum_helpdesk/objects/<model("mum_helpdesk.mum_helpdesk"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mum_helpdesk.object', {
#             'object': obj
#         })
