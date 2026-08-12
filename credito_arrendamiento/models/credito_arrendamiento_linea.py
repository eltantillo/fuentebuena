# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class CreditoArrendamientoLinea(models.Model):
    _name = 'credito.arrendamiento.linea'
    _description = 'Línea de amortización de crédito de arrendamiento'
    _order = 'credito_id, periodo'

    credito_id = fields.Many2one('credito.arrendamiento', string='Crédito', required=True, ondelete='cascade', index=True)
    partner_id = fields.Many2one(related='credito_id.partner_id', string='Cliente', store=True, readonly=True)
    currency_id = fields.Many2one(related='credito_id.currency_id', string='Moneda', readonly=True)
    external_ref = fields.Char(string='ID externo')

    periodo = fields.Integer(string='Semanalidad', required=True)
    fecha_vencimiento = fields.Date(string='Fecha de vencimiento', required=True)
    estado = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
        ('parcial', 'Parcial'),
        ('vencida', 'Vencida'),
    ], string='Estado', default='pendiente', required=True)
    pago_recurrente = fields.Boolean(string='Pago recurrente')
    pago_periodico = fields.Monetary(string='Pago periódico')
    monto_comision_reactivacion = fields.Monetary(string='Comisión por reactivación')
    monto_pagos_aplicados = fields.Monetary(string='Pagos aplicados')
    monto_pendiente = fields.Monetary(string='Monto a pagar')

    _sql_constraints = [
        ('credito_periodo_uniq', 'unique(credito_id, periodo)',
         'Ya existe una semanalidad con ese número para este crédito.'),
    ]
