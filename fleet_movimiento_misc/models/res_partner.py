from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    fleet_movimiento_misc_ids = fields.One2many('fleet.movimiento.misc', 'conductor_id', string='Movimientos como conductor')
    fleet_movimiento_misc_count = fields.Integer(string='Movimientos', compute='_compute_fleet_movimiento_misc_count')

    @api.depends('fleet_movimiento_misc_ids')
    def _compute_fleet_movimiento_misc_count(self):
        for partner in self:
            partner.fleet_movimiento_misc_count = len(partner.fleet_movimiento_misc_ids)

    def action_view_fleet_movimiento_misc(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Movimientos'),
            'res_model': 'fleet.movimiento.misc',
            'view_mode': 'list,form',
            'domain': [('conductor_id', '=', self.id)],
            'context': {'default_conductor_id': self.id},
        }
