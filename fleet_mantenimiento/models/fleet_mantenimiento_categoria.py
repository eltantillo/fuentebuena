from odoo import fields,models,api


class FleetMantenimientoCategoria(models.Model):
    _name = 'fleet.mantenimiento.categoria'

    name = fields.Char(
        string='Nombre',
    )