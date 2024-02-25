# -*- coding: utf-8 -*-
# from odoo import http


# class StateCity(http.Controller):
#     @http.route('/state_city/state_city/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/state_city/state_city/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('state_city.listing', {
#             'root': '/state_city/state_city',
#             'objects': http.request.env['state_city.state_city'].search([]),
#         })

#     @http.route('/state_city/state_city/objects/<model("state_city.state_city"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('state_city.object', {
#             'object': obj
#         })
