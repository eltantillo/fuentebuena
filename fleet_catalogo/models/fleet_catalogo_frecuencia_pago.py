from odoo import models, fields, api


class FleetCatalogoFrecuenciaPago(models.Model):
    _name = 'fleet.catalogo.frecuencia.pago'
    _description = 'Frecuencia de pago'

    name = fields.Char(
        string='Frecuencia de pago'
    )