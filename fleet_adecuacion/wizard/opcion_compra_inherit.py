from odoo import  fields,models,api


class OpcionCompraInherit(models.TransientModel):
    _inherit = 'fleet.opcion.compra'

    def get_gps_importe(self, vehicle_id):
        adecuacion_gps = self.env['fleet.adecuacion.catalogo'].search([
            ('name', '=', 'GPS')
        ], limit=1)

        adecuacion = self.env['fleet.adecuacion'].search([
            ('adecuacion_id', '=', adecuacion_gps.id),
            ('vehiculo_id', '=', vehicle_id)
        ], limit=1)

        return adecuacion.importe if adecuacion else 0

    def get_gnv_importe(self, vehicle):
        if not vehicle.es_gnv:
            return 0
        adecuacion_gnv = self.env['fleet.adecuacion.catalogo'].search([
            ('name', '=', 'GNV')
        ], limit=1)
        adecuacion = self.env['fleet.adecuacion'].search([
            ('adecuacion_id', '=', adecuacion_gnv.id),
            ('vehiculo_id', '=', vehicle.id)
        ], limit=1)
        return adecuacion.importe if adecuacion else 0