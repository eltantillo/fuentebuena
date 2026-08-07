from odoo import fields,models,api


class OdometroInheritFleet(models.Model):
    _inherit = 'fleet.vehicle'

    mostrar_actualizar_odometro = fields.Boolean(
        string='Mostrar Actualizar Odometro',
        compute='_compute_ver_boton',
    )

    def _compute_ver_boton(self):
        flotilla_pilotea = self.env['fleet.customer.flotilla'].search([('name','=', 'Arrendamiento Pilotea')])
        if self.flotilla_id.id  == flotilla_pilotea.id:
            self.mostrar_actualizar_odometro = False
        else:
            self.mostrar_actualizar_odometro = True

    def odometro_actualizar(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'actualizar.odometro',
            'name': 'Actualizar Odometro',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('fleet_odometro.actualizar_odometro_view_form').id,
            'context': {'default_vehiculo_id': self.id}
        }