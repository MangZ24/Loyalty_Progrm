# -*- coding: utf-8 -*-
from odoo import http

# class PosLoyalty(http.Controller):
#     @http.route('/pos_loyalty/pos_loyalty/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_loyalty/pos_loyalty/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_loyalty.listing', {
#             'root': '/pos_loyalty/pos_loyalty',
#             'objects': http.request.env['pos_loyalty.pos_loyalty'].search([]),
#         })

#     @http.route('/pos_loyalty/pos_loyalty/objects/<model("pos_loyalty.pos_loyalty"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_loyalty.object', {
#             'object': obj
#         })