from odoo import http
from odoo.http import request
from werkzeug.exceptions import BadRequest


class FormularioProspectoController(http.Controller):

    @http.route(['/participa'], type='http', auth='public', website=True, csrf=False)
    def mostrar_formulario(self, **kw):
        convenios = request.env['formulario.convenio'].sudo().search([])
        response = request.render('formulario.template_formulario_prospecto', {
            'convenios': convenios,
        })
        response.headers['X-Frame-Options'] = 'ALLOWALL'
        return response


    @http.route(['/participa/submit'], type='http', auth='public', website=True, csrf=False)
    def submit_formulario(self, **post):
        nombre = post.get('nombre')
        apellido = post.get('apellido')
        rfc = post.get('rfc')
        celular = post.get('celular')
        confirmacion = post.get('confirmacion_celular')
        convenio_id = post.get('convenio_id')
        terminos = post.get('terminos_condiciones')
        if not (nombre and apellido and rfc and celular and confirmacion and convenio_id):
            raise BadRequest('Faltan datos obligatorios')
        if celular != confirmacion:
            raise BadRequest('Los números de celular no coinciden')
        if not terminos:
            raise BadRequest('Debes aceptar términos y condiciones')
        request.env['formulario.prospecto'].sudo().create({
            'nombre': nombre,
            'apellido': apellido,
            'rfc': rfc,
            'celular': celular,
            'confirmacion_celular': confirmacion,
            'convenio_id': int(convenio_id),
            'terminos_condiciones': True if terminos else False,
        })
        return request.redirect('/gracias')