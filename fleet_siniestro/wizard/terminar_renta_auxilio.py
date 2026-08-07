from odoo import fields,models,api


class TerminarRentaAuxilio(models.Model):
    _name = 'terminar.renta.auxilio'


    etapa_disponible = fields.Many2one(
        comodel_name='fleet.vehicle.state',
        string='Etapa Disponibile',
        compute='_compute_etapa_disponible',
    )

    def _compute_etapa_disponible(self):
        etapa_disponible = self.env['fleet.vehicle.state'].search([('name','=', 'Disponible')])
        for record in self:
            record.etapa_disponible = etapa_disponible.id


    def action_terminar_renta_auxilio(self):
        vehiculo = self.env['fleet.vehicle'].browse(self.env.context.get('default_vehiculo_id'))
        registro = self.env['fleet.siniestro.renta.auxilio.track'].search([('vehiculo_renta_id','=', vehiculo.id),('estado','=', 'active')], limit=1)
        if registro:
            registro.write({
                'fecha_final': fields.Datetime.now(),
                'estado': 'finalizado'
            })
            vehiculo.driver_id = False
            vehiculo.state_id = self.etapa_disponible.id