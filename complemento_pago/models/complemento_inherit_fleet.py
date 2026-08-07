from odoo import models,api,fields


class ComplementoInheritFleet(models.Model):

    _inherit = "fleet.vehicle"

    complemento_ids = fields.One2many(
        comodel_name='complemento.pago',
        inverse_name='fleet_vehicle_id',
    )