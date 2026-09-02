# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class CreditoArrendamientoPlanPagoLinea(models.Model):
    _name = 'credito.arrendamiento.plan.pago.linea'
    _description = 'Línea de periodo de plan de pago'
    _order = 'plan_pago_id, periodo'

    plan_pago_id = fields.Many2one('credito.arrendamiento.plan.pago', string='Plan de pago', required=True, ondelete='cascade', index=True)
    currency_id = fields.Many2one(related='plan_pago_id.currency_id', string='Moneda', readonly=True)

    periodo = fields.Integer(string='Periodo', required=True)
    fecha_vencimiento = fields.Date(string='Fecha de vencimiento', required=True)
    estado = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
        ('parcial', 'Parcial'),
        ('vencida', 'Vencida'),
    ], string='Estado', default='pendiente')

    monto_prometido = fields.Monetary(string='Monto prometido')
    monto_pagado_promesa = fields.Monetary(string='Monto pagado')
    monto_pendiente_promesa = fields.Monetary(string='Monto pendiente')

    monto_generado_cobranza = fields.Monetary(string='Monto generado')
    monto_pagado_cobranza = fields.Monetary(string='Monto pagado')
    monto_pendiente_cobranza = fields.Monetary(string='Monto pendiente')

    _plan_periodo_uniq = models.Constraint(
        'unique(plan_pago_id, periodo)',
        'Ya existe un periodo con ese número para este plan de pago.',
    )
