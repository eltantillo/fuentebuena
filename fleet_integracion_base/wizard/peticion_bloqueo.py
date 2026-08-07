from odoo import fields,models,api
import logging

_logger = logging.getLogger(__name__)


class PeticionBloqueo(models.TransientModel):
    _name = 'peticion.bloqueo'

    def action_confirm(self):
        type =  self.env.context.get('default_type')
        vehiculo_id = self.env.context.get('default_vehiculo_id')
        vehiculo = self.env['fleet.vehicle'].browse(vehiculo_id)
        if type == 'bloqueo':
            self.bloquear_unidad(vehiculo)
        elif type == 'desbloqueo':
            _logger.info("DEntro de desvloqueo")
            self.desbloquear_unidad(vehiculo)


    def bloquear_unidad(self, vehiculo):
        pass

    def desbloquear_unidad(self, vehiculo):
        pass
