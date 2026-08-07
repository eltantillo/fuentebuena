from odoo import http
from odoo.http import request
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import Forbidden

class CalculadoraController(http.Controller):

    @http.route(['/calculadora'], type='http', auth='public', website=True, csrf=False)
    def mostrar_formulario(self, **kw):
        response = request.render('calculadora.calculadora_template', {})
        response.headers['X-Frame-Options'] = 'ALLOWALL'
        return response