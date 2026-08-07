from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FleetPolizaFleet(models.Model):
    _inherit = 'fleet.vehicle'

    poliza_ids = fields.One2many(
        comodel_name='fleet.poliza',
        inverse_name='vehiculo_id',
        string='Poliza'
    )
    num_polizas = fields.Integer(
        string='Num. Polizas',
        compute='_compute_num_polizas',
    )

    def _compute_num_polizas(self):
        for record in self:
            polizas = self.env['fleet.poliza'].search_count([('vehiculo_id', '=', record.id)])
            record.num_polizas = polizas


    def write(self, vals):
        etapa_disponible = self.env['fleet.vehicle.state'].search([('es_estapa_disponible', '=', True)], limit=1)
        res = super(FleetPolizaFleet, self).write(vals)
        if 'state_id' in vals:
            if vals['state_id'] == etapa_disponible.id and len(self.poliza_ids) < 1:
                raise ValidationError("Se requiere al menos una póliza de seguro para pasar a Disponible")


    def return_action_to_poliza(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.poliza',
            'name': 'Polizas',
            'view_mode': 'list,form',
            'taget': 'new',
            'domain': [('vehiculo_id', '=', self.id)],
            'context': {'create': False},
        }