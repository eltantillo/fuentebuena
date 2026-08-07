from odoo import  models, fields, api


class FleetCompraInheritVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    orden_compra_id = fields.Many2one(
        comodel_name='fleet.orden.compra',
        string='Orden de compra',
        tracking=True,
    )