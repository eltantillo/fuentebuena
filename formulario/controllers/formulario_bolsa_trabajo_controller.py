import base64

from odoo import http
from odoo.http import request
from werkzeug.exceptions import BadRequest

class FormularioBolsaTrabajoController(http.Controller):

    @http.route(['/bolsa-trabajo'], type='http', auth='public', website=True, csrf=False)
    def mostrar_formulario(self, **kw):
        area = request.env['bolsa.trabajo.area'].sudo().search([])
        response = request.render('formulario.template_formulario_bolsa_trabajo', {
            'areas': area,
        })
        response.headers['X-Frame-Options'] = 'ALLOWALL'
        return response

    @http.route(['/bolsa-trabajo/submit'], type='http', auth='public', website=True, csrf=False)
    def submit_formulario(self, **post):
        upload_file = request.httprequest.files.get('cv')
        if upload_file:
            file_content = upload_file.read()
            encoded_file = base64.b64encode(file_content)
            file_name = upload_file.filename
        else:
            encoded_file = ''
            file_name = ''
        if post.get('name') and post.get('telefono') and post.get('correo') and post.get('asunto') and post.get('cv'):
            request.env['formulario.bolsa.trabajo'].sudo().create({
                'nombre': post.get('name'),
                'telefono': post.get('telefono'),
                'correo': post.get('correo'),
                'area_id':int(post.get('area_id')),
                'asunto': post.get('asunto'),
                'cv': encoded_file,
                'cv_filename': file_name
            })
            return request.redirect('/gracias_submit')
        else:
            raise BadRequest('Faltan datos')