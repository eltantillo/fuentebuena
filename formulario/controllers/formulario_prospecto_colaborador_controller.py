from odoo import http
from odoo.http import request
from werkzeug.exceptions import BadRequest


class FormularioProspectoColaboradorController(http.Controller):
    @http.route('/prospeccion', type='http', auth='public', website=True)
    def formulario_prospecto_colaborador(self, **kwargs):
        convenios = request.env['formulario.convenio'].sudo().search([])
        puestos = request.env['formulario.puesto.trabajo'].sudo().search([])
        actividades = request.env['formulario.actividad'].sudo().search([])
        return request.render('formulario.template_formulario_prospecto_colaborador', {
            'convenios': convenios,
            'puestos': puestos,
            'actividades': actividades,
        })


    @http.route('/prospeccion/submit', type='http', auth='public', website=True, csrf=True)
    def formulario_prospecto_colaborador_submit(self, **post):
        nombre = post.get('nombre')
        apellido = post.get('apellido')
        rfc = post.get('rfc')
        celular = post.get('celular')
        confirmacion = post.get('confirmacion_celular')
        gerente_name = post.get('nombre_gerente_vendedor')
        puesto_id = post.get('puesto_id')
        convenio_id = post.get('convenio_id')
        actividad_id = post.get('actividad_id')
        if not (nombre and apellido and rfc and celular and confirmacion and convenio_id):
            raise BadRequest('Faltan datos obligatorios')
        if celular != confirmacion:
            raise BadRequest('Los números de celular no coinciden')
        request.env['formulario.prospecto.colaborador'].sudo().create({
            'nombre': nombre,
            'apellido': apellido,
            'rfc': rfc,
            'celular': celular,
            'confirmacion_celular': confirmacion,
            'nombre_gerente': gerente_name,
            'puesto_id': int(puesto_id),
            'convenio_id': int(convenio_id),
            'actividad_id': int(actividad_id),
        })
        return request.redirect('/gracias')