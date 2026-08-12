from odoo import fields,models,api
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class GestionCaidoInheritFleet(models.Model):

    _inherit = "fleet.vehicle"

    btn_confirmar_recepcion = fields.Boolean(
        string="Confirmar Recepcion",
        default=True
    )
    edit_vehicle = fields.Boolean(
        string="Editar Vehiculo",
        default=True
    )

    def return_ultima_gestion(self, vehiculo_id):
        gestion_search = self.env['gestion.caido'].search(
            [('vehiculo_id', '=', vehiculo_id),
             ('active', '=', True)],
            limit=1
        )
        return gestion_search

    def return_ultimo_track(self, gestion_id):
        track_search = self.env['gestion.caido.track'].search(
            [('gestion_id', '=', gestion_id)],
            limit=1, order='id desc'
        )
        return track_search


    def construir_diccionario(self, gestion,fecha_finalizacion,evento):
        diccionario_gestion = {
            'gestion_id': gestion,
            'fecha_inicio': fields.Datetime.now(),
            'fecha_finalizacion': fecha_finalizacion,
            'evento': evento,
        }
        return diccionario_gestion

    def confirmar_recepcion(self):
        etapas_validas = ['En gestión','En posesión','Recuperado']
        gestion = self.env['gestion.caido'].search([
            ('vehiculo_id', '=', self.id),
            ('estado_id.name', 'in', etapas_validas),],
        limit=1, order='id desc')
        gestion_finalizacion = self.env['gestion.caido.estado'].search([('name', '=', 'Finalizado')], limit=1)
        if gestion:
            return {
                'type': 'ir.actions.client',
                'tag': 'gc_posesion_posesion',
                'name': 'Recepción de Vehículo',
                'target': 'new',
                'context': {
                    'active_id': gestion.id,
                    'active_model': gestion._name,
                    'new_stage': gestion_finalizacion.id,
                    'new_stage_vehiculo': gestion.etapa_destino_vehiculo_id.id,
                    'vehiculo_id': self.id,
                    'type': 'recuperacion',
                }
            }
        else:
            _logger.info('No se puede recepcionar: No se encontró gestión activa para vehiculo_id=%s', self.id)


    def notificacion_email_recuperado(self):
        pass

    def write(self, vals):
        etapa_disponible = self.env['fleet.vehicle.state'].search([('es_estapa_disponible','=', True)], limit=1).id
        for record in self:
            if not self.env.context.get('from_wizard'):
                if not record.edit_vehicle and ('state_id' in vals or 'tag_ids' in vals):
                    raise UserError(
                        'Este vehículo no puede ser editado actualmente.'
                        'Se requiere subir la evidencia de Gestión'
                    )
            if 'state_id' in vals and vals['state_id']  == etapa_disponible:
                gestion_ultima = self.env['gestion.caido'].sudo().search([('vehiculo_id', '=', record.id)], limit=1, order='id desc')
                if gestion_ultima:
                    ultimo_evento = gestion_ultima.track_ids[-1]
                    if ultimo_evento.evento == 'Mantenimiento Finalizado':
                        gestion_ultima.registrar_evento(f"Vehículo pasa a Disponible", True)
        return super().write(vals)