# -*- coding: utf-8 -*-
# Catálogo de Tipos de Empleado (Base, Confianza, Seguridad Pública, Eventual, Jubilado, Pensionado)
from odoo import models, fields

class FbEmployeeType(models.Model):
    _name = 'fb.employee.type'
    _description = 'Tipo de Empleado'

    name = fields.Char(string='Tipo de Empleado', required=True)
    code = fields.Char(string='Código')
    active = fields.Boolean(string='Activo', default=True)
