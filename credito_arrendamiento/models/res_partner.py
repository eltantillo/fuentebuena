# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credito_arrendamiento_ids = fields.One2many('credito.arrendamiento', 'partner_id', string='Créditos de arrendamiento')
    credito_arrendamiento_count = fields.Integer(string='Créditos', compute='_compute_credito_arrendamiento_count')

    @api.depends('credito_arrendamiento_ids')
    def _compute_credito_arrendamiento_count(self):
        for partner in self:
            partner.credito_arrendamiento_count = len(partner.credito_arrendamiento_ids)

    def action_view_credito_arrendamientos(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Créditos de arrendamiento'),
            'res_model': 'credito.arrendamiento',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
