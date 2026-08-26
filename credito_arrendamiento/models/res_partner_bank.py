# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    clabe_pago = fields.Char(string='CLABE de pago', size=18)

    @api.constrains('clabe_pago')
    def _check_clabe_pago(self):
        for bank in self:
            if bank.clabe_pago and (len(bank.clabe_pago) != 18 or not bank.clabe_pago.isdigit()):
                raise ValidationError(_('La CLABE de pago debe tener exactamente 18 dígitos numéricos.'))
