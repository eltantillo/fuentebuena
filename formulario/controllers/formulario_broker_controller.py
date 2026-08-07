from odoo import http
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

class FormularioBrokerController(http.Controller):

    @http.route(['/broker-form'], type='http', auth='public', website=True, csrf=False)
    def mostrar_formulario(self, **kw):
        estados = request.env['res.country.state'].sudo().search([('country_id', '=', 'MX')])
        municipios = request.env['municipio'].sudo().search([])
        num_emps = request.env['formulario.broker']._fields['num_empleado'].selection
        response = request.render('formulario.template_formulario_broker', {
            'estados': estados,
            'municipios': municipios,
            'num_emps': num_emps,
        })
        response.headers['X-Frame-Options'] = 'ALLOWALL'
        return response

    @http.route(['/broker-form/submit'], type='http', auth='public', website=True, csrf=False)
    def submit_formulario(self, **post):
        if not post.get('website_check'):
            terminos = post.get('autorizacion_datos')
            request.env['formulario.broker'].sudo().create({
                'nombre': post.get('name'),
                'telefono': post.get('telefono'),
                'correo': post.get('correo'),
                'estado_id': post.get('estado_id'),
                'municipio_id': int(post.get('municipio_id')),
                'num_empleado': post.get('num_empleado'),
                'acepto_uso_datos': True if terminos else False,
            })
            return request.redirect('/gracias_submit')