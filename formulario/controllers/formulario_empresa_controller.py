from odoo import http
from odoo.http import request

class FormularioEmpresaConfigController(http.Controller):

    @http.route(['/empresas/<string:slug>'], type='http', auth='public', website=True)
    def formulario_empresa_config(self, slug=None, **kwargs):
        empresa = request.env['formulario.empresa.config'].sudo().search([('slug', '=', slug)], limit=1)
        if not empresa:
            return request.not_found()
        return request.render('formulario.template_formulario_empresa', {'empresa': empresa})



    @http.route(['/empresas/<string:slug>/submit'], type='http', auth='public', website=True)
    def formulario_empresa_submit(self, slug=None, **post):
        empresa = request.env['formulario.empresa.config'].sudo().search([('slug', '=', slug)], limit=1)
        if not empresa:
            return request.not_found()
        nombre_completo = post.get('nombre_completo')
        numero_telefono = post.get('numero_telefono')
        correo = post.get('correo_electronico')
        empresa_id = empresa.id
        rfc = post.get('rfc')
        autorizacion_datos = post.get('autorizacion_datos')
        request.env['formulario.empresa'].sudo().create({
            'nombre_completo': nombre_completo,
            'numero_telefono': numero_telefono,
            'correo': correo,
            'empresa_id': empresa_id,
            'rfc': rfc,
            'autorizacion_datos': autorizacion_datos,
        })
        return request.redirect('/gracias')