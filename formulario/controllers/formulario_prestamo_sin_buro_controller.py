from odoo import http
from odoo.http import request
from werkzeug.exceptions import BadRequest

import logging
_logger = logging.getLogger(__name__)

class FormularioPrestamoSinBuroController(http.Controller):

    @http.route(['/solicita-tu-credito'], type='http', auth='public', website=True, csrf=False)
    def mostrar_formulario(self, **kw):
        puesto_ocupado = request.env['puesto.ocupado'].sudo().search([])
        productos = request.env['formulario.producto'].sudo().search([])
        estados = request.env['res.country.state'].sudo().search([('country_id', '=', 'MX')])
        convenios = request.env['formulario.ayuntamiento'].sudo().search([])
        respuesta = request.env['formulario.prestamo.sin.buro']._fields['es_trabajador_ayuntamiento'].selection
        response = request.render('formulario.template_formulario_prestamo_sin_buro',{
            'puesto_ocupado': puesto_ocupado,
            'estados': estados,
            'convenios': convenios,
            'respuesta': respuesta,
            'productos': productos,
        })
        response.headers['X-Frame-Options'] = 'ALLOWALL'
        return response

    @http.route(['/solicita-tu-credito/submit'], type='http', auth='public', website=True, csrf=False)
    def submit_formulario(self, **post):
        if post.get('name') and post.get('apellido') and post.get('correo') and post.get('telefono') and post.get('estado') and post.get('puesto_id'):
            terminos = post.get('terminos_condiciones')
            request.env['formulario.prestamo.sin.buro'].create({
                'nombre': post.get('name'),
                'apellido': post.get('apellido'),
                'correo': post.get('correo'),
                'telefono': post.get('telefono'),
                'estado_id': post.get('estado'),
                'puesto_ocupado_id': int(post['puesto_id']) if post.get('convenio_id') else False,
                'es_trabajador_ayuntamiento': post.get('respuesta'),
                'convenio_id': int(post['convenio_id']) if post.get('convenio_id') else False,
                'acepto_uso_datos': True if terminos else False,
            })
            return request.redirect('/gracias')
        else:
            raise BadRequest('Faltan datos')