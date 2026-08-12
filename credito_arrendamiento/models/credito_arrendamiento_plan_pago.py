# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class CreditoArrendamientoPlanPago(models.Model):
    _name = 'credito.arrendamiento.plan.pago'
    _description = 'Plan de pago de crédito de arrendamiento'
    _rec_name = 'external_ref'

    credito_id = fields.Many2one('credito.arrendamiento', string='Crédito', required=True, ondelete='cascade', index=True)
    partner_id = fields.Many2one(related='credito_id.partner_id', string='Cliente', store=True, readonly=True)
    currency_id = fields.Many2one(related='credito_id.currency_id', string='Moneda', readonly=True)
    external_ref = fields.Char(string='ID externo')

    estatus = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('activo', 'Activo'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ], string='Estatus', default='pendiente')
    fecha_inicio = fields.Date(string='Fecha inicial del plan')
    fecha_fin = fields.Date(string='Fecha final del plan')
    numero_periodos = fields.Integer(string='Número de periodos')

    saldo_total = fields.Monetary(string='Saldo total')
    saldo_pagado = fields.Monetary(string='Saldo pagado')
    saldo_restante = fields.Monetary(string='Saldo restante')
    avance = fields.Float(string='Avance (%)')
    saldo_vencido = fields.Monetary(string='Saldo vencido')
    ahorro_total = fields.Monetary(string='Ahorro total en el préstamo')
    monto_liquidar = fields.Monetary(string='Monto para liquidar')

    saldo_vencido_sin_gastos_cobranza = fields.Monetary(string='Saldo vencido sin gastos de cobranza')
    saldo_gastos_cobranza = fields.Monetary(string='Saldo de gastos de cobranza')
    saldo_no_devengado = fields.Monetary(string='Saldo no devengado')
    condonaciones = fields.Monetary(string='Condonaciones')
    descuento = fields.Monetary(string='Descuento')
    intereses_posteriores_plan = fields.Monetary(string='Intereses posteriores al plan')
    ajuste_redondeo = fields.Monetary(string='Ajuste por redondeo')
    total_pagar = fields.Monetary(string='Total a pagar')
    pago_periodico_monto = fields.Monetary(string='Pago periódico')

    linea_ids = fields.One2many('credito.arrendamiento.plan.pago.linea', 'plan_pago_id', string='Periodos del plan')
