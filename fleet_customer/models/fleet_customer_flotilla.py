from odoo import models, fields, api

class FleetCustomerFlotilla(models.Model):
    _name = 'fleet.customer.flotilla'
    _description = 'Módulo personalizado para registrar las flotillas para los vehículos'

    name = fields.Char(
        string='Nombre de flotilla',
    )
    active = fields.Boolean('Active', default=True, tracking=True)