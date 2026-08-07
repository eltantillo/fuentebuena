from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)

class FleetSiniestroInheritFleet(models.Model):
    _inherit = 'fleet.vehicle'

    num_siniestros = fields.Integer(
        string='Num. Siniestros',
        compute='_compute_num_siniestros',
    )
    siniestro_ids = fields.One2many(
        comodel_name='fleet.siniestro',
        inverse_name='vehiculo_id',
        string='Siniestros'
    )


    def _compute_num_siniestros(self):
        for record in self:
            siniestros = self.env['fleet.siniestro'].search_count([('vehiculo_id', '=', record.id)])
            record.num_siniestros = siniestros


    def return_action_to_siniestro(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.siniestro',
            'name': 'Siniestros',
            'view_mode': 'list,form',
            'taget': 'new',
            'domain': [('vehiculo_id', '=', self.id)],
            'context': {'create': False},
        }