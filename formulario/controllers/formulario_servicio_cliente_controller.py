from odoo import http
from odoo.http import request
from werkzeug.exceptions import BadRequest

class FormularioServicioClienteController(http.Controller):

    @http.route(['/servicio-al-cliente'], type='http', auth="public", website=True, csrf=False)
    def mostrar_formulario(self,**kw):
        response = request.render('formulario.template_formulario_servicio_cliente',{})
        response.headers['X-Frame-Options'] = 'ALLOWALL'
        return response

    @http.route(['/servicio-al-cliente/submit'], type='http', auth="public", website=True, csrf=False)
    def submit_formulario(self,**post):
        if post.get('name') and post.get('apellido') and post.get('correo') and post.get('telefono') and post.get('mensaje'):
            request.env['formulario.servicio.cliente'].create({
                'nombre': post.get('name'),
                'apellido': post.get('apellido'),
                'correo': post.get('correo'),
                'telefono': post.get('telefono'),
                'mensaje': post.get('mensaje'),
            })
            return request.redirect('/gracias')
        else:
            raise BadRequest('Faltan datos')