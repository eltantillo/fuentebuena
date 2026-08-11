# -*- coding: utf-8 -*-

from odoo import models, fields

class FbAgreementPartner(models.Model):
    _name = 'fb.agreement.partner'
    _description = 'Personas que apoyaron la firma del convenio'

    partner_id = fields.Many2one('res.partner', string='Contacto', required=True)
    fb_phone = fields.Char(string='Teléfono')
    fb_email = fields.Char(string='Correo electrónico')
    fb_availability_care = fields.Char(string='Disponibilidad de atención.')
    agreement_id = fields.Many2one('fb.agreement', string='Convenio', ondelete='cascade')