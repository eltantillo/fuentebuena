import base64

from odoo import http
from odoo.http import request
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import Forbidden

class FormularioBolsaTrabajoController(http.Controller):

    @http.route(['/mapa-interactivo'], type='http', auth='public', website=True, csrf=False)
    def mostrar_formulario(self, **kw):
        response = request.render('mapa.template_mapa_interactivo', {})
        response.headers['X-Frame-Options'] = 'ALLOWALL'
        return response