# -*- coding: utf-8 -*-
from odoo import models, fields

class FbAgreementStage(models.Model):
    _name = 'fb.agreement.stage'
    _description = 'Etapa del Convenio'
    _order = 'sequence, id'

    name = fields.Char(string='Nombre de la Etapa', required=True, translate=True)
    sequence = fields.Integer(string='Secuencia', default=10)
    fold = fields.Boolean(string='Plegado en Kanban')
