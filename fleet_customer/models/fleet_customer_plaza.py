from odoo import fields, models, api


class FleetCustomerPlaza(models.Model):
    _name = 'fleet.customer.plaza'
    _description = 'Módulo personalizado para registrar las plazas para los vehículos'

    name = fields.Char(
        string='Nombre de plaza',
    )