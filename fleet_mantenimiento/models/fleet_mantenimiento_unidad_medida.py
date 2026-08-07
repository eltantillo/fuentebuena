from odoo import models, fields, api


class FleetMantenimientoUnidadMedida(models.Model):
    _name = 'fleet.mantenimiento.unidad.medida'
    _description = 'Unidad de medida'

    name = fields.Char(
        string="Unidad de medida"
    )
    active = fields.Boolean('Active', default=True, tracking=True)