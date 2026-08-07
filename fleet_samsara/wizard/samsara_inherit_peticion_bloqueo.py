from odoo import fields,models,api


class SamaraInheritPeticionBloqueo(models.TransientModel):

    _inherit = "peticion.bloqueo"

    def bloquear_unidad(self, vehiculo):
        if vehiculo:
            if vehiculo.external_gps_provider == "samsara":
                msg,estado = self.env['fleet.samsara'].block_vehicle(vehiculo.external_gps_id)
                vals = self.vals_create(vehiculo, "bloqueo", msg, estado)
                self.env['integracion.base.bloqueo'].create(vals)


    def vals_create(self, vehiculo, tipo, msg, estado):
        vals = {
           'tipo': tipo,
           'vehiculo_id': vehiculo.id,
           'msg_error': msg
        }
        if not estado:
            vals['estado_peticion'] = 'error'
        return vals