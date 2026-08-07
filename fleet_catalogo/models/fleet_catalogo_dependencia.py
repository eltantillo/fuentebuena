from odoo import fields, models, api


class FleetCatalogoDependencia(models.Model):
    _name = 'fleet.catalogo.dependencia'
    _description = 'Dependencias'

    name = fields.Char(
        string='Dependencia',
        required=True
    )