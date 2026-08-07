from odoo import  fields,models,api


class TecnoInheritACSiniestro(models.Model):
    _inherit='atencion.cliente.siniestro'

    ultima_ubicacion = fields.Char(
        string='Lugar'
    )

    def obtener_ubicacion(self):
        fleet_v = self.env['fleet.vehicle']
        data = fleet_v.consultar_vehiculo(0)
        vehiculos = {
            v['SERIE']:v['UBICACION'] for v in data
        }
        ubicacion = vehiculos.get(self.vin_sn)
        if ubicacion:
            self.ultima_ubicacion = fleet_v.process_ubicacion(ubicacion)
        else:
            self.ultima_ubicacion = False