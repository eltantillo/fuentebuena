from odoo import models, fields, api

class FleetMantenimientoTipo(models.Model):
    _name = 'fleet.mantenimiento.tipo'
    _description = 'Tipo de mantenimiento'

    name = fields.Char(
        string="Tipo de mantenimiento"
    )
    active = fields.Boolean('Active', default=True, tracking=True)