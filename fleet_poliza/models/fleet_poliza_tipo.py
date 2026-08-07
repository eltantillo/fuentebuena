from odoo import models,api,fields


class FleetPolizaTipo(models.Model):

    _name = 'fleet.poliza.tipo'

    name = fields.Char(
        string='Nombre'
    )