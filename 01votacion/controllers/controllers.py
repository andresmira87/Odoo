# -*- coding: utf-8 -*-
# from odoo import http


# class Votacion2(http.Controller):
#     @http.route('/01votacion/01votacion', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/01votacion/01votacion/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('01votacion.listing', {
#             'root': '/01votacion/01votacion',
#             'objects': http.request.env['01votacion.01votacion'].search([]),
#         })

#     @http.route('/01votacion/01votacion/objects/<model("01votacion.01votacion"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('01votacion.object', {
#             'object': obj
#         })

