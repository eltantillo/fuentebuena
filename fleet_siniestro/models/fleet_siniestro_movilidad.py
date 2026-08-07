from odoo import models, fields, api


class FleetSiniestroMovilidad(models.Model):
    _name = 'fleet.siniestro.movilidad'
    _description = 'Siniestro'

    name = fields.Char(
        string='Movilidad'
    )
    active = fields.Boolean('Active', default=True, tracking=True)