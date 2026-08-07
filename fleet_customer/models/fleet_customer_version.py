from odoo import fields, models, api


class FleetCustomerVersion(models.Model):
    _name = "fleet.customer.version"
    _description = "Version"

    name = fields.Char(
        string="Version"
    )
    model_id = fields.Many2one(
        comodel_name="fleet.vehicle.model",
        string="Modelo"
    )