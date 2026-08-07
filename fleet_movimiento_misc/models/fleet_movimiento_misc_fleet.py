from odoo import models, fields, api


class FleetMovimientoMiscFleet(models.Model):
    _inherit = 'fleet.vehicle'

    movimiento_ids = fields.One2many(
        comodel_name='fleet.movimiento.misc',
        inverse_name='vehiculo_id',
        string='Movimientos',
    )