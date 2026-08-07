from odoo import http
from odoo.http import request
from werkzeug.exceptions import BadRequest

class ProspectoAnimadorController(http.Controller):
    @http.route('/experienciadigital', type='http', auth='public', website=True)
    def formulario_animador(self, **kwargs):
        convenios = request.env['formulario.convenio'].sudo().search([])
        return request.render(
            'formulario.template_formulario_prospecto_animador',
            {
                'convenios': convenios
            }
        )

    @http.route('/experienciadigital/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def submit_animador(self, **post):
        nombre = post.get('nombre')
        apellido = post.get('apellido')
        rfc = post.get('rfc')
        celular = post.get('celular')
        confirmacion = post.get('confirmacion_celular')
        convenio_id = post.get('convenio_id')
        uso_datos = post.get('terminos_condiciones')
        if not (nombre and apellido and rfc and celular and confirmacion and convenio_id):
            raise BadRequest('Faltan datos obligatorios')
        if celular != confirmacion:
            raise BadRequest('Los números de celular no coinciden')
        if not uso_datos:
            raise BadRequest('Debes aceptar el uso de datos personales')
        request.env['formulario.prospecto.animador'].sudo().create({
            'nombre': nombre,
            'apellido': apellido,
            'rfc': rfc,
            'celular': celular,
            'confirmacion_celular': confirmacion,
            'convenio_id': int(convenio_id),
            'uso_datos': True if uso_datos else False,
        })
        return request.redirect('/gracias')