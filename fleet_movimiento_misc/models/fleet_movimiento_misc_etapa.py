from odoo import models, fields, api


class FleetMovimientoMiscEtapa(models.Model):
    _name = 'fleet.movimiento.misc.etapa'
    _description = 'Fleet Movimiento Misc Etapa'

    name = fields.Char(
        string='Etapa'
    )
    active = fields.Boolean('Active', default=True, tracking=True)