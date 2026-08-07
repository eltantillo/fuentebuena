from odoo import models,fields, api

class InheritUser(models.Model):
    _inherit = "agenda.entrega"

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Usuario',
        default=lambda self: self.env.user,
    )

    plaza_ids = fields.Many2many(
        comodel_name='fleet.customer.plaza',
        string='Plazas del usuario',
        compute='_compute_plazas',
        store=True,
    )

    @api.depends('user_id','user_id.plaza_ids')
    def _compute_plazas(self):
        for record in self:
            record.plaza_ids = record.user_id.plaza_ids