from odoo import fields,models,api


class FleetSamsaraInheritFleet(models.Model):
    _inherit = 'fleet.vehicle'

    external_gps_provider = fields.Selection(
        selection_add=[
            ('samsara', 'Samsara'),
        ]
    )


