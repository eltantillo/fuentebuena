# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FbAuthorizedSignaturesLettersAdmission(models.Model):
    _name = 'fb.authorized.signatures.letters.admission'
    _description = 'Firmas autorizadas en cartas de ingreso'

    partner_id = fields.Many2one('res.partner', string='Nombre', required=True)
    position = fields.Char(string='Puesto', required=True)
    active = fields.Boolean(string='Activo', default=True)
    agreement_id = fields.Many2one('fb.agreement', string='Convenio', ondelete='cascade')