from odoo import fields, models, api


class FleetTramiteMotivoPago(models.Model):
    _name = 'fleet.tramite.motivo.pago'
    _description = 'Motivo de pago'

    name = fields.Char(
        string='Motivo de pago'
    )