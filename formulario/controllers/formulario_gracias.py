from odoo import http
from odoo.http import request

class FormularioGraciasController(http.Controller):

    @http.route(['/gracias'], type='http', auth='public', website=True, csrf=False)
    def gracias(self, **kw):
        response = request.render('formulario.template_gracias', {})
        response.headers['X-Frame-Options'] = 'ALLOWALL'
        return response

    @http.route(['/gracias_submit'], type='http', auth='public', website=True, csrf=False)
    def gracias_submit(self, **kw):
        response = request.render('formulario.template_gracias_submit', {})
        response.headers['X-Frame-Options'] = 'ALLOWALL'
        return response