from odoo import models, fields, api


class FleetContratoMotivoCancelacion(models.Model):
    _name = 'fleet.contrato.motivo.cancelacion'
    _description = 'Motivo de cancelación del contrato'

    name = fields.Char(
        string='Motivo de cancelación'
    )