# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FbPayrollClosingDays(models.Model):
    _name = 'fb.payroll.closing.days'
    _description = 'Dias de cierre de nomina.'

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código')
    active = fields.Boolean(string='Activo', default=True)