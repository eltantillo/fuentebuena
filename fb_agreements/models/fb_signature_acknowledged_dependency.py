# -*- coding: utf-8 -*-

from odoo import models, fields

class FbAgreementPartner(models.Model):
    _inherit = 'fb.agreement.partner'
    _name = 'fb.signature.acknowledged.dependency'
    _description = 'Firmas de enterado por la dependencia '

    fb_position = fields.Char(string='Puesto', required=True)
    fb_firm = fields.Char(string='Firma', help='Firma')
    fb_date = fields.Date(string='Fecha', help='Fecha')