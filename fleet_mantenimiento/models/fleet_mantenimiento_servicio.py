from odoo import models, fields, api

class FleetMantenimientoServicio(models.Model):
    _name = 'fleet.mantenimiento.servicio'
    _description = 'Fleet Mantenimiento Servicios'

    name = fields.Char(
        string="Servicio"
    )
    mantenimiento_ids = fields.Many2many(
        comodel_name='fleet.mantenimiento.tipo',
        string='Tipo de mantenimiento'
    )
    active = fields.Boolean('Active', default=True, tracking=True)