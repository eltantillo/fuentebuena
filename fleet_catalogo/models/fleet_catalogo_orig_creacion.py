from odoo import models, fields, api


class FleetCatalogoOrigCreacion(models.Model):
    _name = 'fleet.catalogo.orig.creacion'
    _description = 'Origen de creacion'

    name = fields.Char(
        string='Origen de creacion'
    )