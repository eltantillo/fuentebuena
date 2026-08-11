from odoo import fields,models,api


class FleetCustomerUbicacion(models.Model):

    _name = 'fleet.customer.ubicacion'

    name = fields.Char(
        string='Nombre'
    )