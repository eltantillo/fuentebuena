from odoo import models, fields, api

class FleetTramiteTipo(models.Model):
    _name = 'fleet.tramite.tipo'
    _description = 'Tipo de tramite'

    name = fields.Char(
        string='Tipo'
    )
    active = fields.Boolean('Active', default=True, tracking=True)