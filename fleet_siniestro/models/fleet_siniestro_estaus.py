from odoo import models, fields, api

class FleetSiniestroEstatus(models.Model):
    _name = 'fleet.siniestro.estatus'
    _description = 'Estatus del siniestro'

    name = fields.Char(
        string='Estatus'
    )
    active = fields.Boolean('Active', default=True, tracking=True)