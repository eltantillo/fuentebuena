import time

from odoo import fields,models,api
from datetime import datetime
import pytz
import logging

_logger = logging.getLogger(__name__)

class cm_conector_simply_cola(models.Model):
    _name = 'cm.conector.simply.cola'

    booking_id = fields.Integer(
        string='Booking_id',
    )
    state = fields.Selection(
        selection=[
            ('pendiente', 'Pendiente'),
            ('procesando', 'Procesando'),
            ('hecho', 'Hecho'),
            ('error', 'Error'),
        ],
        default='pendiente',
    )
    operation_type = fields.Selection(
        selection=[
            ('crear','Crear'),
            ('cancelar','Cancelar'),
            ('actualizar','Actualizar'),
        ]
    )
    retries = fields.Integer(
        string='Retries',
        default=0,
    )
    error_msg = fields.Char(
        string='Error Msg',
    )

    def procesar_create(self):
        _logger.info("Iniciando 'procesar_create' para %s registros.", len(self))
        for cita in self:
            _logger.info("Procesando cita (CREAR) - ID: %s, Booking ID: %s", cita.id, cita.booking_id)
            cita.write({'state': 'procesando'})
            try:
                with self.env.cr.savepoint():
                    self.env['cita.mantenimiento'].process_cita(cita.booking_id)
                    cita.state = 'hecho'
                    _logger.info("Cita ID %s procesada correctamente (CREAR).", cita.id)
            except Exception as e:
                nuevos_retry = cita.retries + 1
                _logger.error("Error en procesar_create para Cita ID %s. Intento actual: %s. Error: %s", cita.id,
                              nuevos_retry, str(e))
                cita.write({
                    'retries': nuevos_retry,
                    'error_msg': str(e),
                    'state': 'error' if nuevos_retry >= 5 else 'pendiente'
                })

    def procesar_actualizar(self):
        _logger.info("Iniciando 'procesar_actualizar' para %s registros.", len(self))
        for cita in self:
            _logger.info("Procesando cita (ACTUALIZAR) - ID: %s, Booking ID: %s", cita.id, cita.booking_id)
            cita.write({'state': 'procesando'})
            try:
                with self.env.cr.savepoint():
                    self.env['cita.mantenimiento'].update_cita(cita.booking_id)
                    cita.state = 'hecho'
                    _logger.info("Cita ID %s actualizada correctamente.", cita.id)
            except Exception as e:
                nuevos_retry = cita.retries + 1
                _logger.error("Error en procesar_actualizar para Cita ID %s. Intento actual: %s. Error: %s", cita.id,
                              nuevos_retry, str(e))
                cita.write({
                    'retries': nuevos_retry,
                    'error_msg': str(e),
                    'state': 'error' if nuevos_retry >= 5 else 'pendiente'
                })

    def procesar_cancelar(self):
        _logger.info("Iniciando 'procesar_cancelar' para %s registros.", len(self))
        for cita in self:
            _logger.info("Procesando cita (CANCELAR) - ID: %s, Booking ID: %s", cita.id, cita.booking_id)
            cita.write({'state': 'procesando'})
            try:
                with self.env.cr.savepoint():
                    self.env['cita.mantenimiento'].cancel_cita_simply(cita.booking_id)
                    cita.state = 'hecho'
                    _logger.info("Cita ID %s cancelada correctamente.", cita.id)
            except Exception as e:
                nuevos_retry = cita.retries + 1
                _logger.error("Error en procesar_cancelar para Cita ID %s. Intento actual: %s. Error: %s", cita.id,
                              nuevos_retry, str(e))
                cita.write({
                    'retries': nuevos_retry,
                    'error_msg': str(e),
                    'state': 'error' if nuevos_retry >= 5 else 'pendiente'
                })

    def procesar_uno_uno(self):
        tz = pytz.timezone('America/Mexico_City')
        ahora = datetime.now(tz)
        if ahora.hour in [0, 1, 2,3]:
            _logger.info("Ejecución omitida en 'procesar_uno_uno' debido a la restricción horaria (%s:00 hs).",
                         ahora.hour)
            return

        _logger.info("Iniciando ejecución de 'procesar_uno_uno' a las %s.", ahora.strftime('%Y-%m-%d %H:%M:%S'))

        citas_create = self.search([('state', '=', 'pendiente'), ('operation_type', '=', 'crear')], limit=1)
        if citas_create:
            _logger.info("Se encontraron %s citas pendientes para CREAR.", len(citas_create))
            citas_create.procesar_create()
            time.sleep(2)

        citas_update = self.search([('state', '=', 'pendiente'), ('operation_type', '=', 'actualizar')], limit=1)
        if citas_update:
            _logger.info("Se encontraron %s citas pendientes para ACTUALIZAR.", len(citas_update))
            citas_update.procesar_actualizar()
            time.sleep(2)
        citas_cancelar = self.search([('state', '=', 'pendiente'), ('operation_type', '=', 'cancelar')], limit=1)
        if citas_cancelar:
            _logger.info("Se encontraron %s citas pendientes para CANCELAR.", len(citas_cancelar))
            citas_cancelar.procesar_cancelar()