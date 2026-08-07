from odoo import models, fields, api


class FleetCustomerMotivoBaja(models.Model):
    _name = 'fleet.customer.motivo.baja'
    _description = 'Motivo de baja'

    name = fields.Char(
        string='Motivo de baja',
    )