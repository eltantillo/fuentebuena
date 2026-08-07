from odoo import fields, models, api


class FleetMovimientoMiscMotivo(models.Model):
    _name = 'fleet.movimiento.misc.motivo'
    _description = 'Motivos de movimientos miscelaneos'

    name = fields.Char(
        string='Motivo',
        required=True
    )
    active = fields.Boolean('Active', default=True, tracking=True)