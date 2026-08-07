from odoo import models, fields, api


class FleetCatalogoOrigCreacion(models.Model):
    _inherit = 'fleet.mantenimiento'
    _description = 'Origen de creacion'

    origen_id = fields.Many2one(
        comodel_name='fleet.catalogo.orig.creacion',
        string='Origen de creacion'
    )

