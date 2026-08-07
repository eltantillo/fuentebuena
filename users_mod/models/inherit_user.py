from odoo import models,fields, api

class InheritUser(models.Model):
    _inherit = "res.users"

    flotilla_ids = fields.Many2many(
        string='Flotilla',
        comodel_name='fleet.customer.flotilla',
        private=False
    )
    plaza_ids = fields.Many2many(
        string='Plaza',
        comodel_name='fleet.customer.plaza',
        private=False
    )
    id_usuario = fields.Integer(
        string='Usuario',
    )