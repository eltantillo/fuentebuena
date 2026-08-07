from odoo import models, fields, api


class FleetCustomerFuenteFondero(models.Model):
    _name = 'fleet.customer.fuente.fondeo'
    _description = 'Fuente de Fondeo'
    rec_name = 'name'

    name = fields.Char(
        string='Fuente de Fondeo',
    )