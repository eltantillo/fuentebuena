# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _


class CreditoArrendamiento(models.Model):
    _name = 'credito.arrendamiento'
    _description = 'Crédito de arrendamiento'
    _inherit = ['mail.thread']
    _rec_name = 'external_ref'

    partner_id = fields.Many2one('res.partner', string='Cliente', required=True, tracking=True)
    vehiculo_id = fields.Many2one('fleet.vehicle', string='Automóvil', tracking=True)
    external_ref = fields.Char(string='ID del crédito', index=True, tracking=True)

    fecha_disposicion = fields.Date(string='Fecha de disposición')
    frecuencia = fields.Selection([
        ('semanal', 'Semanal'),
        ('catorcenal', 'Catorcenal'),
        ('quincenal', 'Quincenal'),
        ('mensual', 'Mensual'),
    ], string='Frecuencia', default='semanal')
    tasa_interes_anual_sin_iva = fields.Float(string='Tasa de interés anual sin IVA (%)')
    tasa_interes_anual_con_iva = fields.Float(string='Tasa de interés anual con IVA (%)')
    cat = fields.Float(string='CAT (%)')

    saldo_principal_no_exigible = fields.Monetary(string='Saldo de principal no exigible')
    saldo_exigible = fields.Monetary(string='Saldo exigible')
    pagos_anticipados_acumulados = fields.Monetary(string='Pagos anticipados acumulados')
    dias_mora = fields.Integer(string='Días de mora')
    estado = fields.Selection([
        ('vigente', 'Vigente'),
        ('castigado', 'Castigado'),
        ('liquidado', 'Liquidado'),
        ('cancelado', 'Cancelado'),
    ], string='Estado del préstamo', default='vigente', tracking=True)

    currency_id = fields.Many2one('res.currency', string='Moneda', default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)

    linea_ids = fields.One2many('credito.arrendamiento.linea', 'credito_id', string='Tabla de amortización')
    plan_pago_ids = fields.One2many('credito.arrendamiento.plan.pago', 'credito_id', string='Planes de pago')
    plan_pago_count = fields.Integer(string='Planes de pago', compute='_compute_plan_pago_count')

    _sql_constraints = [
        ('external_ref_uniq', 'unique(external_ref)', 'Ya existe un crédito con ese ID externo.'),
    ]

    @api.depends('plan_pago_ids')
    def _compute_plan_pago_count(self):
        for credito in self:
            credito.plan_pago_count = len(credito.plan_pago_ids)
