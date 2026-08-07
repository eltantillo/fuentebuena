from odoo import fields, api, models
import logging

_logger = logging.getLogger(__name__)

class RolesPiloteaInheritFleet(models.Model):
    _inherit = 'fleet.vehicle'

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Usuario',
        default=lambda self: self.env.user,
    )
    plaza_ids = fields.Many2many(
        comodel_name='fleet.customer.plaza',
        compute='_compute_plazas',
        string='Plazas del usuario',
        store=True,
    )
    gerente_flota_id = fields.Many2one(
        comodel_name='res.users',
        string='Gerente de flota',
        compute='_compute_gerente_flota',
    )


    def _compute_gerente_flota(self):
        group_go = self.env['res.groups'].search([('name', '=', 'Gerente de operaciones')])
        for record in self:
            if record.id:
                gerente_flota = self.env['res.users'].search([('group_ids', 'in', [group_go.id]),('plaza_ids','in', [record.plaza_id.id]),('flotilla_ids','in', [record.flotilla_id.id])])
                _logger.info(gerente_flota)
                for g in gerente_flota:
                    if len(g.plaza_ids) > 2 and g.flotilla_ids:
                        record.gerente_flota_id = False
                    else:
                        record.gerente_flota_id = g.id
                        break
            else:
                record.gerente_flota_id = False


    @api.depends('user_id','user_id.plaza_ids')
    def _compute_plazas(self):
        for record in self:
            record.plaza_ids = record.user_id.plaza_ids