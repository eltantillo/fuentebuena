from odoo import fields,models,api


class FleetVehicleInheritRenta(models.Model):
    _inherit = 'fleet.vehicle'


    def renta_auxilio(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'renta.auxilio',
            'name': 'Renta Auxilio',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('fleet_siniestro.fleet_siniestro_renta_auxilio_form').id,
            'context': {'default_vehiculo_id': self.id}
        }