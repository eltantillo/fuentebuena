from odoo import fields,models,api


class OdometroInheritMantenimiento(models.Model):
    _inherit = 'fleet.mantenimiento'

    def _actualizar_odometro(self):
        res = super()._actualizar_odometro()
        wizard = self.env['actualizar.odometro'].sudo().create({
            'vehiculo_id': self.vehiculo_id.id,
            'km_actualizar': self.km_entrada
        })
        wizard.actualizar_odometro()