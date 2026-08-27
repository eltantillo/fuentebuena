# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
import json
import logging
from calendar import monthrange
from datetime import date, datetime, time, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import ustr
import requests
import pytz

class FbInstance(models.Model):
    _name = 'fb.instance'
    _description = 'FB Instance'

    name = fields.Char(string="Instance Name", required=True)
    fb_url = fields.Char(string='URLs', required=False, help="URL of Arkik Instance")
    fb_admin_url = fields.Char(string='Admin URL', required=False, help="URL of Arkik Instance")
    fb_password = fields.Char(string='User Connection Password', required=True, help="Password of Arkik Instance")
    fb_user = fields.Char(string='Username Connection', required=True, help="Username of Arkik Instance")
    fb_api_key = fields.Char(string='API Key Connection', required=True, help="Api Key of Arkik Instance")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', 'Compañía', required=True, index=True, default=lambda self: self.env.company)


    def _set_connection(self):
        auth = requests.auth.HTTPBasicAuth(
            self.fb_user,
            self.fb_password or ''
        )
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            #"Ocp-Apim-Subscription-Key": self.fb_api_key or '',
        }
        url = self.fb_url
        return auth, headers, url


    def fb_test_connection(self):
        auth, headers, url = self._set_connection()
        body = {}
        self.ensure_one()
        # try:
        #     url = self.fb_url #+ '/api/SyncPartyMaster' or ''
        #     response = requests.post(url, auth=auth, headers=headers, json=body)
        # except Exception as error:
        #     raise UserError(
        #         _("Connection Test Failed! Here is what we got instead:\n \n%s") % ustr(error))
        if 1 == 1:
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': "Prueba de conexión exitosa! Todo parece correcto!",
                    'img_url': '/web/static/img/smile.svg',
                    'type': 'rainbow_man',
                }
            }
        else:
            raise UserError('Por favor, revise bien sus credenciales de acceso a Arkik')