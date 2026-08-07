from odoo import models, fields, api


class FleetContratoCondicionVehiculo(models.Model):
    _name = 'fleet.contrato.condicion.vehiculo'
    _description = 'Condicion Vehiculo'

    name = fields.Char(
        string='Condicion Vehiculo'
    )