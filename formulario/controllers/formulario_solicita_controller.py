from odoo import http
from odoo.http import request
from werkzeug.exceptions import BadRequest

class FormularioSolicitaController(http.Controller):

    @http.route(['/solicita'], type='http', auth="public", website=True, csrf=False)
    def mostrar_formulario(self, **kw):
        estados = request.env['res.country.state'].sudo().search([('country_id', '=', 'MX')])
        medios = request.env['formulario.solicita.medio'].sudo().search([])
        response = request.render('formulario.template_formulario_solicita',{
            'estados': estados,
            'medios': medios,
        })
        response.headers['X-Frame-Options'] = 'ALLOWALL'
        return response

    @http.route(['/solicita/submit'], type='http', auth="public", website=True, csrf=False)
    def submit_formulario(self, **post):
        if post.get('nombre') and post.get('rfc') and post.get('telefono') and post.get('correo') and post.get('estado'):
            vals = {
                'nombre': post.get('nombre'),
                'rfc': post.get('rfc'),
                'telefono': post.get('telefono'),
                'correo': post.get('correo'),
                'estado_id': post.get('estado'),
                'solicita_medio_id': post.get('medio'),
            }
            if post.get('motivotext'):
                vals['solicita_medio_otro'] = post.get('motivotext')
            request.env['formulario.solicita'].create(vals)
            return request.redirect('/gracias')
        else:
            raise BadRequest('Faltan datos')