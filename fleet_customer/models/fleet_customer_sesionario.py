from odoo import models, fields, api


class FleetCustomerSesionario(models.Model):
    _name = 'fleet.customer.sesionario'
    _description = 'Sesionario'
    rec_name = 'name'

    name = fields.Char(
        string='Sesionario',
    )