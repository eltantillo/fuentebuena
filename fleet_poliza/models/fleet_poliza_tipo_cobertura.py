from odoo import models, fields, api


class FleetPolizaTipoCobertura(models.Model):
    _name = 'fleet.poliza.tipo.cobertura'
    _description = 'Tipo de cobertura'

    name = fields.Char(
        string='Tipo de cobertura'
    )
    active = fields.Boolean('Active', default=True, tracking=True)