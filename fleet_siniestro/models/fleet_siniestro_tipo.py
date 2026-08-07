from odoo import models, fields


class FleetSiniestroTipo(models.Model):
    _name = 'fleet.siniestro.tipo'
    _description = 'Tipo de Siniestro'

    name = fields.Char(
        string='Tipo de Siniestro'
    )
    active = fields.Boolean('Active', default=True, tracking=True)
