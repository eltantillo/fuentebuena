# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FbBranch(models.Model):
    _name = 'fb.branch'
    _description = 'Sucursales'

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código')
    active = fields.Boolean(string='Activo', default=True)