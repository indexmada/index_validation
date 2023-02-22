# -*- coding: utf-8 -*-
# from odoo import http


# class ComplexeValidation(http.Controller):
#     @http.route('/complexe_validation/complexe_validation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/complexe_validation/complexe_validation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('complexe_validation.listing', {
#             'root': '/complexe_validation/complexe_validation',
#             'objects': http.request.env['complexe_validation.complexe_validation'].search([]),
#         })

#     @http.route('/complexe_validation/complexe_validation/objects/<model("complexe_validation.complexe_validation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('complexe_validation.object', {
#             'object': obj
#         })
