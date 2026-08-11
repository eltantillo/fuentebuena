# -*- coding: utf-8 -*-

from odoo import models, fields

class FbAgreementUserTechnicalSpecifications(models.Model):
    _name = 'fb.agreement.user.technical.specifications'
    _description = 'Firma del convenio | Ficha tecnica'

    user_id = fields.Many2one('res.users', string='Nombre', required=True)
    fb_email = fields.Char(string='Correo electrónico', related='user_id.login')
    fb_position = fields.Char(string='Puesto', related='user_id.partner_id.function')
    agreement_id = fields.Many2one('fb.agreement', string='Convenio', ondelete='cascade')