# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _
from odoo.tools.misc import formatLang


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

    proximo_cargo_fecha = fields.Date(
        string='Próximo cargo (fecha)', compute='_compute_proximo_cargo', store=True)
    proximo_cargo_monto = fields.Monetary(
        string='Próximo cargo (monto)', compute='_compute_proximo_cargo', store=True)
    renta_periodica_label = fields.Char(
        string='Renta (según frecuencia)', compute='_compute_renta_periodica_label')

    _sql_constraints = [
        ('external_ref_uniq', 'unique(external_ref)', 'Ya existe un crédito con ese ID externo.'),
    ]

    @api.depends('plan_pago_ids')
    def _compute_plan_pago_count(self):
        for credito in self:
            credito.plan_pago_count = len(credito.plan_pago_ids)

    @api.depends('linea_ids.estado', 'linea_ids.periodo', 'linea_ids.fecha_vencimiento', 'linea_ids.pago_periodico')
    def _compute_proximo_cargo(self):
        for credito in self:
            proxima_linea = credito.linea_ids.filtered(lambda l: l.estado == 'pendiente').sorted('periodo')[:1]
            credito.proximo_cargo_fecha = proxima_linea.fecha_vencimiento if proxima_linea else False
            credito.proximo_cargo_monto = proxima_linea.pago_periodico if proxima_linea else 0.0

    @api.depends('proximo_cargo_monto', 'frecuencia')
    def _compute_renta_periodica_label(self):
        frecuencia_labels = dict(self._fields['frecuencia'].selection)
        for credito in self:
            if credito.proximo_cargo_monto and credito.frecuencia:
                monto_str = formatLang(self.env, credito.proximo_cargo_monto, currency_obj=credito.currency_id)
                credito.renta_periodica_label = '%s / %s' % (monto_str, frecuencia_labels.get(credito.frecuencia, ''))
            else:
                credito.renta_periodica_label = False
