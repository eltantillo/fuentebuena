from odoo import http
from odoo.http import request
import json
from odoo import SUPERUSER_ID
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)
import requests



class ArkikControllers(http.Controller):

    @http.route('/fb/agreements', type='json', auth='public', methods=['POST'], csrf=False)
    def fb_agreements(self, **kwargs): #Modelo 'arkik.daily.orders'

        superuser_env = request.env(user=SUPERUSER_ID)
        #instance = superuser_env['arkik.instance'].search([],limit=1)
        try:
            data = request.dispatcher.jsonrequest if hasattr(request, 'dispatcher') else request.params
            if not data:
                data = kwargs  # Por si acaso entrara algo por query params

            data_string = json.dumps(data)

            record = superuser_env['fb.integration.log'].create({
                'data': data_string,
            })

        except Exception as e:
            print(f"❌ Error al procesar la petición: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            }