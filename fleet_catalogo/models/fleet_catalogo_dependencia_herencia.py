from odoo import models, fields, api


class FleetCatalogoDependHerenciaMovMisc(models.Model):
    _inherit = 'fleet.movimiento.misc'

    dependencia_id = fields.Many2one(
        comodel_name='fleet.catalogo.dependencia',
        string='Dependencia',
    )
