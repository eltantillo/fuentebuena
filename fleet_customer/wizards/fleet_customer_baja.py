from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class FleetBaja(models.TransientModel):
    _name = 'fleet.customer.baja'
    _description = 'Baja de vehiculo'

    motivo_id = fields.Many2one(
        comodel_name='fleet.customer.motivo.baja',
        string='Motivo de baja'
    )


    def action_confirm(self):
        vehicle_id = self.env.context.get('active_id')
        vehicle = self.env['fleet.vehicle'].browse(vehicle_id)
        motivo = self.motivo_id
        vehicle.sudo().write({
            'motivo_baja_id': motivo,
            'baja': True,
            'fecha_baja': fields.Date.today()
        })