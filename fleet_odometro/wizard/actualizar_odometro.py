from odoo import fields,models,api


class ActualizarOdometro(models.TransientModel):
    _name = 'actualizar.odometro'

    vehiculo_id = fields.Many2one(
        string='Vehiculo',
        comodel_name='fleet.vehicle'
    )
    km_actualizar = fields.Float(
        string='Nuevo kilometraje',
    )

    def actualizar_odometro(self):
        etapa_registrado = self.env['actualizar.odometro.etapa'].search([('name', '=', 'Registrado')], limit=1)
        odometro_regis = self.env['fleet.vehicle.odometer'].search([('vehicle_id','=',self.vehiculo_id.id)], limit=1, order='id desc')
        if odometro_regis:
            odometro_regis.value = self.km_actualizar
        self.vehiculo_id.odometro_mod = self.km_actualizar
        self.env['fleet.tecno.actualizar.odometro'].create({
            'vehicle_id': self.vehiculo_id.id,
            'cliente': self.vehiculo_id.driver_id.name,
            'vin': self.vehiculo_id.vin_sn,
            'odometro': self.km_actualizar,
            'etapa_id': etapa_registrado.id,
        })
        self.vehiculo_id.message_post(
            body=f"⏲ Odómetro actualizado a {self.km_actualizar} km.",
            message_type="comment",
            subtype_xmlid="mail.mt_comment"
        )