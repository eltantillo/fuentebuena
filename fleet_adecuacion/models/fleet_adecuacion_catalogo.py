from odoo import models, fields, api


class fleet_adecuacion_catalogo(models.Model):
    _name = 'fleet.adecuacion.catalogo'
    _description = 'Catalogo de Adecuaciones'
    _rec_name = 'name'

    name = fields.Char(
        string='Adecuación',
    )
