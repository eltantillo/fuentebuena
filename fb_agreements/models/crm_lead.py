# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    fb_aprecia = fields.Boolean(
        string='Aprecia',
        default=False, copy=False, related='company_id.fb_aprecia',
        help='Si está marcado, la empresa es Aprecia')

    fb_institution_type_id = fields.Many2one('fb.crm.institution.type', string='Tipo de institución',
        help='Institución relacionada con la oportunidad.')

    fb_agreement_ids = fields.One2many(
        'fb.agreement',
        'crm_lead_id',
        string='Convenios'
    )

    # Estado del convenio más reciente (campo computado)
    fb_agreement_status = fields.Char(
        string='Estado de convenio',
        compute='_compute_fb_agreement_status',
        store=True
    )

    # --- PESTAÑA INDICADORES: BASE DE TRABAJADORES ---
    fb_workers_trust = fields.Integer(string='Confianza', default=0)
    fb_workers_base = fields.Integer(string='Base', default=0)
    fb_workers_eventual = fields.Integer(string='Eventuales', default=0)
    fb_workers_fees = fields.Integer(string='Honorarios', default=0)

    fb_workers_total = fields.Integer(
        string='Total trabajadores',
        compute='_compute_fb_workers_total',
        store=True
    )

    # --- PESTAÑA INDICADORES: FORTALEZA FINANCIERA ---
    fb_population_count = fields.Integer(string='Número habitantes', default=0)

    # Aplican solo si el tipo de institución es 'municipal'
    fb_own_income = fields.Monetary(string='Ingresos propios', currency_field='company_currency')
    fb_branch_28_contributions = fields.Monetary(string='Aportaciones ramo 28', currency_field='company_currency')
    fb_branch_33_contributions = fields.Monetary(string='Aportaciones ramo 33', currency_field='company_currency')

    # --- CONTROL DE TARJETA KANBAN (COLOR DE BORDE) ---
    fb_opportunity_type = fields.Selection([
        ('new', 'Nuevo'),
        ('renewal', 'Renovación')
    ], string='Tipo de Oportunidad', default='new', compute='_compute_fb_opportunity_type', store=True)

    # --- COMPUTOS Y LÓGICA ---

    @api.depends('fb_workers_trust', 'fb_workers_base', 'fb_workers_eventual', 'fb_workers_fees')
    def _compute_fb_workers_total(self):
        for lead in self:
            lead.fb_workers_total = (
                    lead.fb_workers_trust +
                    lead.fb_workers_base +
                    lead.fb_workers_eventual +
                    lead.fb_workers_fees
            )

    @api.depends('fb_agreement_ids', 'fb_agreement_ids.stage_id','fb_agreement_ids.write_date', 'fb_agreement_ids.create_date')
    def _compute_fb_agreement_status(self):
        for lead in self:
            if lead.fb_agreement_ids:
                # Obtiene el convenio creado o modificado más recientemente
                latest_agreement = \
                lead.fb_agreement_ids.sorted(key=lambda r: r.write_date or r.create_date or datetime.min, reverse=True)[0]
                lead.fb_agreement_status = latest_agreement.stage_id.name if latest_agreement.stage_id else 'Sin Etapa'
            else:
                lead.fb_agreement_status = 'No Operando'

    @api.depends('fb_agreement_ids')
    def _compute_fb_opportunity_type(self):
        for lead in self:
            # Si tiene más de 1 convenio o histórico de convenios, se clasifica como Renovación
            if len(lead.fb_agreement_ids) > 1:
                lead.fb_opportunity_type = 'renewal'
            else:
                lead.fb_opportunity_type = 'new'

    def cron_opportunity_sweep(self):
        stage_id = self.env['crm.stage'].search([], order='sequence asc', limit=1)
        lead_ids = self.search([('stage_id.is_won', '=', True)])
        lead_ids.write({
            'color': 1,
            'stage_id': stage_id.id
        })
        return