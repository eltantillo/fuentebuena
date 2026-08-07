from odoo import http
from odoo.http import request
import time
import uuid
import jwt
import logging

_logger = logging.getLogger(__name__)

class DahsboardTableauController(http.Controller):

    @http.route('/consul-token', type='json', auth='user', methods=['POST'])
    def consultar_token(self):
        access_key_id = request.env['ir.config_parameter'].sudo().get_param('dashboard_tableau.access_key_id')
        secret_id = request.env['ir.config_parameter'].sudo().get_param('dashboard_tableau.secret_id')
        secret_value = request.env['ir.config_parameter'].sudo().get_param('dashboard_tableau.secret_value')
        user_email = request.env['ir.config_parameter'].sudo().get_param('dashboard_tableau.user_email')
        tableau_domain = request.env['ir.config_parameter'].sudo().get_param('dashboard_tableau.tableau_domain')
        view_url = request.env['ir.config_parameter'].sudo().get_param('dashboard_tableau.view_url')
        payload = {
            "iss": access_key_id,
            "exp": int(time.time()) + 600,  # Expira en 10 min
            "jti": str(uuid.uuid4()),
            "aud": 'tableau',
            "sub": user_email,
            "scp": ['tableau:views:embed']
        }
        headers = {
            "kid": str(secret_id),
            "iss": str(access_key_id),
        }
        token = jwt.encode(payload, secret_value, algorithm='HS256', headers=headers)
        return {"token": token}