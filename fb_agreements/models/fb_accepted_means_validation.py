# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FbAcceptedMeansValidation(models.Model):
    _name = 'fb.accepted.means.validation'
    _description = 'Medios aceptados de validación.'

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código')
    active = fields.Boolean(string='Activo', default=True)