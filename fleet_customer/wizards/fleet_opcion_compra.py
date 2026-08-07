from odoo import fields, models, api
import base64

import logging

_logger = logging.getLogger(__name__)

class FleetOpcionCompra(models.TransientModel):
    _name = 'fleet.opcion.compra'

    subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True,
        inverse='_inverse_subtotal',
    )
    gnv = fields.Float(
        string='GNV',
        compute='_compute_gnv',
        store=True,
        inverse='_inverse_gnv',
    )
    gps = fields.Float(
        string='GPS',
        compute='_compute_gps',
        store=True,
        inverse='_inverse_gps',
    )
    subtotal_gps = fields.Float(
        string='Subtotal con GPS',
        compute='_compute_subtotal_gps',
    )
    subtotal_gps_gnv = fields.Float(
        string='Subtotal GPS + GNV',
        compute='_compute_subtotal_gps_gnv',
    )
    valor_residual_adquisicion = fields.Float(
        string='Valor residual',
        compute='_compute_valor_residual_adquisicion',
    )

    def get_gps_importe(self, vehicle_id):
        return 0

    def get_gnv_importe(self, vehicle):
        return 0

    def _compute_gps(self):
        vehicle_id = self.env.context.get('active_id')
        for record in self:
            record.gps = record.get_gps_importe(vehicle_id)

    def _compute_gnv(self):
        vehicle_id = self.env.context.get('active_id')
        vehicle = self.env['fleet.vehicle'].browse(vehicle_id)
        for record in self:
            record.gnv = record.get_gnv_importe(vehicle)

    def _inverse_gps(self):
        pass

    def _inverse_gnv(self):
        pass

    def _inverse_subtotal(self):
        pass

    def _compute_subtotal(self):
        vehicle_id = self.env.context.get('active_id')
        vehicle = self.env['fleet.vehicle'].browse(vehicle_id)
        for record in self:
            if vehicle.importe_adquisicion:
                record.subtotal = vehicle.importe_adquisicion
            else:
                record.subtotal = 0

    @api.depends('subtotal','gps')
    def _compute_subtotal_gps(self):
        for record in self:
            record.subtotal_gps = record.subtotal + record.gps

    @api.depends('subtotal','gps','gnv')
    def _compute_subtotal_gps_gnv(self):
        for record in self:
            record.subtotal_gps_gnv = record.subtotal + record.gps + record.gnv

    @api.depends('subtotal_gps_gnv')
    def _compute_valor_residual_adquisicion(self):
        for record in self:
            record.valor_residual_adquisicion = record.subtotal_gps_gnv * .37


    def crear_opcion_compra(self):
        vehicle_id = self.env.context.get('active_id')
        vehicle = self.env['fleet.vehicle'].browse(vehicle_id)
        vehicle.write({
            'valor_residual_adquisicion': self.valor_residual_adquisicion,
        })
        report_action = self.env.ref('fleet_customer.report_opcion_compra')
        pdf_content, pdf_format = report_action._render_qweb_pdf(report_ref=report_action,res_ids=[vehicle.id])
        vehicle.write({
            'opcion_compra': base64.b64encode(pdf_content),
        })