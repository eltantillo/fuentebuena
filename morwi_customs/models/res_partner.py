# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _

class ResPartner(models.Model):

    _inherit = 'res.partner'

    fleet_customer_plaza_id = fields.Many2one(string='Square', comodel_name='fleet.customer.plaza')
    fleet_vehicle_year = fields.Integer(string='Year')
    fleet_vehicle_salesman = fields.Many2one(string='Salesman', comodel_name='res.partner')
    fleet_vehicle_kilometrage = fields.Integer(string='Kilometrage')
    fleet_customer_producto_id = fields.Many2one(comodel_name='fleet.customer.producto', string='Product Type')
    fleet_siniestro_estatus_id = fields.Many2one(comodel_name='fleet.siniestro.estatus')

    fleet_vehicle_ids = fields.One2many(comodel_name='fleet.vehicle', inverse_name='driver_id', string='Vehicles')
    fleet_vehicle_count = fields.Integer(string='Vehicle Count', compute='_compute_fleet_vehicle_count')

    fleet_vehicle_log_contract_ids = fields.One2many(comodel_name='fleet.vehicle.log.contract', inverse_name='cliente_id', string='Contracts')
    fleet_vehicle_log_contract_count = fields.Integer(string='Contract Count', compute='_compute_fleet_vehicle_log_contract_count')

    fleet_siniestro_ids = fields.One2many(comodel_name='fleet.siniestro', inverse_name='cliente_id', string='Claims')
    fleet_siniestro_count = fields.Integer(string='Claim Count', compute='_compute_fleet_siniestro_count')

    fleet_movimiento_misc_ids = fields.One2many(comodel_name='fleet.movimiento.misc', inverse_name='cliente_id', string='Misc Movements')
    fleet_movimiento_misc_count = fields.Integer(string='Misc Movement Count', compute='_compute_fleet_movimiento_misc_count')

    fleet_poliza_ids = fields.One2many(comodel_name='fleet.poliza', inverse_name='cliente_id', string='Policies')
    fleet_poliza_count = fields.Integer(string='Policy Count', compute='_compute_fleet_poliza_count')

    fleet_tramite_ids = fields.One2many(comodel_name='fleet.tramite', inverse_name='cliente_id', string='Procedures')
    fleet_tramite_count = fields.Integer(string='Procedure Count', compute='_compute_fleet_tramite_count')

    @api.depends('fleet_vehicle_ids')
    def _compute_fleet_vehicle_count(self):
        for partner in self:
            partner.fleet_vehicle_count = len(partner.fleet_vehicle_ids)

    @api.depends('fleet_vehicle_log_contract_ids')
    def _compute_fleet_vehicle_log_contract_count(self):
        for partner in self:
            partner.fleet_vehicle_log_contract_count = len(partner.fleet_vehicle_log_contract_ids)

    @api.depends('fleet_siniestro_ids')
    def _compute_fleet_siniestro_count(self):
        for partner in self:
            partner.fleet_siniestro_count = len(partner.fleet_siniestro_ids)

    @api.depends('fleet_movimiento_misc_ids')
    def _compute_fleet_movimiento_misc_count(self):
        for partner in self:
            partner.fleet_movimiento_misc_count = len(partner.fleet_movimiento_misc_ids)

    @api.depends('fleet_poliza_ids')
    def _compute_fleet_poliza_count(self):
        for partner in self:
            partner.fleet_poliza_count = len(partner.fleet_poliza_ids)

    @api.depends('fleet_tramite_ids')
    def _compute_fleet_tramite_count(self):
        for partner in self:
            partner.fleet_tramite_count = len(partner.fleet_tramite_ids)

    def _action_view_fleet_records(self, res_model, inverse_field, name, editable_default=False):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': name,
            'res_model': res_model,
            'view_mode': 'list,form',
            'domain': [(inverse_field, '=', self.id)],
        }
        if editable_default:
            action['context'] = {'default_%s' % inverse_field: self.id}
        return action

    def action_view_fleet_vehicles(self):
        return self._action_view_fleet_records('fleet.vehicle', 'driver_id', _('Vehicles'), editable_default=True)

    def action_view_fleet_vehicle_log_contracts(self):
        return self._action_view_fleet_records('fleet.vehicle.log.contract', 'cliente_id', _('Contracts'))

    def action_view_fleet_siniestros(self):
        return self._action_view_fleet_records('fleet.siniestro', 'cliente_id', _('Claims'))

    def action_view_fleet_movimiento_miscs(self):
        return self._action_view_fleet_records('fleet.movimiento.misc', 'cliente_id', _('Misc Movements'), editable_default=True)

    def action_view_fleet_polizas(self):
        return self._action_view_fleet_records('fleet.poliza', 'cliente_id', _('Policies'))

    def action_view_fleet_tramites(self):
        return self._action_view_fleet_records('fleet.tramite', 'cliente_id', _('Procedures'))
