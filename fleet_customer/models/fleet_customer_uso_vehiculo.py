from odoo import models, fields, api

class FleetCustomerUsoVehiculo(models.Model):
    _name = 'fleet.customer.uso.vehiculo'
    _description = 'Módulo personalizado para registrar las condiciones de los vehículos'

    name = fields.Char(
        string='Nombre de condicion',
    )