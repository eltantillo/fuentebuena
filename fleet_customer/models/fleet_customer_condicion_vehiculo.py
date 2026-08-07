from odoo import models, fields, api

class FleetCustomerCondicionVehiculo(models.Model):
    _name = 'fleet.customer.condicion.vehiculo'
    _desccription = 'Módulo personalizado para registrar las condiciones para los vehículos'

    name = fields.Char(
        string='Nombre de condicion vehiculo'
    )