from odoo import http
from odoo.http import request
from werkzeug.exceptions import BadRequest

class FormularioRenegociarController(http.Controller):

    @http.route(['/renegociar-deuda'], type='http', auth='public', website=True, csrf=False)
    def mostrar_formulario(self, **kw):
        medios_contacto = request.env['medio.contacto'].sudo().search([])
        puesto_ocupado = request.env['puesto.ocupado'].sudo().search([])
        estados = request.env['formulario.renegociar']._fields['estado'].selection
        response = request.render('formulario.template_formulario_renegociar', {
            'medios_contacto': medios_contacto,
            'puesto_ocupado': puesto_ocupado,
            'estados': estados,
        })
        response.headers['X-Frame-Options'] = 'ALLOWALL'
        return response

    @http.route(['/renegociar-deuda/submit'], type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def submit_formulario(self, **post):
        if post.get('name') and post.get('apellido') and post.get('correo') and post.get('telefono') and post.get('estado') and post.get('puesto_id') and post.get('medio_contacto_id'):
            request.env['formulario.renegociar'].create({
                'nombre': post.get('name'),
                'apellido': post.get('apellido'),
                'correo': post.get('correo'),
                'telefono': post.get('telefono'),
                'estado': post.get('estado'),
                'puesto_ocupado_id': int(post.get('puesto_id')),
                'medio_contacto_id': int(post.get('medio_contacto_id')),
            })
            return request.redirect('/gracias')
        else:
            raise BadRequest('Faltan datos')