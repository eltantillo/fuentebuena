# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CrmInstitutionType(models.Model):
    _name = 'fb.crm.institution.type'
    _description = 'Tipo de Institution'

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código')
    active = fields.Boolean(string='Activo', default=True)