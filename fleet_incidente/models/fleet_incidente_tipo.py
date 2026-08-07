from odoo import models,api,fields


class FleetIncidenteTipo(models.Model):
    _name = 'fleet.incidente.tipo'

    name = fields.Char(
        string="Nombre"
    )
    categoria_agrupacion = fields.Many2one(
        string="Categoria",
        comodel_name='fleet.customer.categoria.agrupacion',
    )
