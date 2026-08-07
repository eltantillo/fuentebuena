from odoo import http
from odoo.http import request
from werkzeug.exceptions import BadRequest

class FormularioDependencia(http.Controller):

    @http.route(['/afilia-tu-institucion'], type='http', auth="public", website=True, csrf=False)
    def mostrar_formulario_dependencia(self, **kwargs):
        categoria_empleado = request.env['puesto.ocupado'].sudo().search([])
        response = request.render('formulario.template_formulario_institucion', {
            'categora_empleado': categoria_empleado,
        })
        response.headers['X-Frame-Options'] = 'ALLOWALL'
        return response

    @http.route('/afilia-tu-institucion/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def submit_animador(self, **post):
        nombre = post.get('nombre_completo')
        telefono = post.get('numero_telefono')
        correo = post.get('correo_electronico')
        dependencia_ayuntamiento = post.get('dependencia_ayuntamiento')
        puesto = post.get('puesto')
        categoria_empleado_id = post.get('categoria_id')
        pertenece_sindicato = post.get('pertenece_sindicato')
        medio_contacto_institucional = post.get('medio_contacto_institucional')
        nombre_contacto = post.get('nombre_contacto')
        puesto_contacto = post.get('puesto_contacto')
        nombre_presidente_municipal = post.get('nombre_presidente_municipal')
        request.env['formulario.dependencia'].sudo().create({
            'nombre_completo': nombre,
            'numero_telefono': telefono,
            'correo_electronico': correo,
            'dependencia_ayuntamiento': dependencia_ayuntamiento,
            'puesto': puesto,
            'categoria_empleado_id': int(categoria_empleado_id),
            'pertenece_sindicato': pertenece_sindicato,
            'medio_contacto_institucional': medio_contacto_institucional,
            'nombre_contacto':nombre_contacto,
            'puesto_contacto':puesto_contacto,
            'nombre_presidente_municipal':nombre_presidente_municipal
        })
        return request.redirect('/gracias')