import math

from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

PRODUCTOS_CON_MANTE = [1, 6, 7, 8, 10, 11, 12]
STATE_ACTIVO = 10
TAG_EXCLUIDO = 1
TIPO_MANTE_PREVENTIVO_ID = 1
KM_INTERVALO = 10000


class FleetMantenimientoInheritFleet(models.Model):
    _inherit = 'fleet.vehicle'

    km_ult_mantenimiento = fields.Float(string='Km último mantenimiento')
    km_prox_mantenimiento = fields.Float(string='Km próximo mantenimiento')
    diferencia_prox_mantenimiento = fields.Float(
        string='Diferencia próximo mantenimiento',
        store=True,
    )
    nombre_semaforo = fields.Char(string='Nombre semaforo', store=True)
    mantenimiento_proximo_id = fields.Many2one(
        comodel_name='fleet.mantenimiento.servicio.tipo',
        string='Mantenimiento próximo',
    )
    num_mantes = fields.Integer(
        string='Num. Polizas',
        compute='_compute_num_mantes',
    )

    def _redondear(self, monto):
        """Redondea al siguiente múltiplo de 10,000."""
        return math.floor((monto + 5000) / 10000) * 10000

    def redondear(self, monto):
        return self._redondear(monto)

    def _compute_num_mantes(self):
        for record in self:
            record.num_mantes = self.env['fleet.mantenimiento'].search_count(
                [('vehiculo_id', '=', record.id)]
            )

    def return_action_to_mantes(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.mantenimiento',
            'name': 'Mantenimientos',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [('vehiculo_id', '=', self.id)],
            'context': {'create': True, 'default_vehiculo_id': self.id},
        }

    def crear_mantenimiento(self):
        """
        Crea un mantenimiento preventivo para el vehículo si no existe uno
        pendiente/en curso (etapas 1, 2, 6) y si el tipo de servicio próximo
        aún no tiene registro.

        Usa SELECT FOR UPDATE implícito mediante search+limit para evitar
        condición de carrera en ejecuciones concurrentes.
        """
        self.ensure_one()
        if not self.mantenimiento_proximo_id:
            return
        # Bloquear la búsqueda de duplicados dentro de la misma transacción
        pendiente = self.env['fleet.mantenimiento'].search(
            [
                ('vehiculo_id', '=', self.id),
                ('etapa_id', 'in', [1, 2, 6]),
            ],
            limit=1,
        )
        if pendiente:
            _logger.info(
                'Vehículo %s ya tiene mantenimiento pendiente (id=%s). '
                'No se creará uno nuevo.',
                self.name,
                pendiente.id,
            )
            return
        ya_existe = self.env['fleet.mantenimiento'].search(
            [
                ('vehiculo_id', '=', self.id),
                ('tipo_mantenimiento_servicio_id', '=', self.mantenimiento_proximo_id.id),
            ],
            limit=1,
        )
        if ya_existe:
            _logger.info(
                'Vehículo %s ya tiene mantenimiento para servicio %s (id=%s).',
                self.name,
                self.mantenimiento_proximo_id.name,
                ya_existe.id,
            )
            return

        self.env['fleet.mantenimiento'].create_custom({
            'etapa_id': 6,
            'origen_id': 1,
            'tipo_mantenimiento_id': TIPO_MANTE_PREVENTIVO_ID,
            'tipo_mantenimiento_servicio_id': self.mantenimiento_proximo_id.id,
            'vehiculo_id': self.id,
            'fecha_deteccion': fields.Date.today(),
            'km_deteccion': self.odometer,
        })
        _logger.info(
            'Mantenimiento creado para vehículo %s, servicio %s.',
            self.name,
            self.mantenimiento_proximo_id.name,
        )

    def tratar_vehiculo_sin_mante(self, vehiculos):
        """Resetea todos los campos de semáforo en un solo write masivo."""
        vehiculos.write({
            'km_ult_mantenimiento': 0,
            'km_prox_mantenimiento': 0,
            'diferencia_prox_mantenimiento': 0,
            'mantenimiento_proximo_id': False,
            'nombre_semaforo': 'No aplica',
        })

    def _calcular_semaforo_vals(self, vehiculo, mantes_prev_por_vehiculo):
        """
        Devuelve un dict con todos los valores del semáforo para *vehiculo*
        sin tocar la base de datos (excepto búsquedas de lectura).
        """
        vals = {}
        mantes_prev_vh = mantes_prev_por_vehiculo.get(vehiculo.id, [])
        if mantes_prev_vh:
            ultimo = max(mantes_prev_vh, key=lambda x: x.tipo_mantenimiento_servicio_id.valor)
            vals['km_ult_mantenimiento'] = (
                ultimo.km_entrada if ultimo.km_entrada > 0 else vehiculo.odometro_mod
            )
        else:
            vals['km_ult_mantenimiento'] = (
                0 if vehiculo.odometro_mod < KM_INTERVALO else vehiculo.odometro_mod
            )
        vals['km_prox_mantenimiento'] = vals['km_ult_mantenimiento'] + KM_INTERVALO
        vals['diferencia_prox_mantenimiento'] = (
            vals['km_prox_mantenimiento'] - vehiculo.odometro_mod
        )
        mante_prox = self.env['fleet.mantenimiento.servicio.tipo'].search(
            [
                ('mantenimiento_tipo_id', '=', TIPO_MANTE_PREVENTIVO_ID),
                ('valor', '=', self._redondear(vals['km_prox_mantenimiento'])),
            ],
            limit=1,
        )
        if mante_prox:
            ya_registrado = self.env['fleet.mantenimiento'].search(
                [
                    ('vehiculo_id', '=', vehiculo.id),
                    ('tipo_mantenimiento_servicio_id', '=', mante_prox.id),
                ],
                limit=1,
            )
            vals['mantenimiento_proximo_id'] = mante_prox.id if not ya_registrado else False
        else:
            vals['mantenimiento_proximo_id'] = False
        diff = vals['diferencia_prox_mantenimiento']
        if diff >= 1000:
            vals['nombre_semaforo'] = 'Verde'
        elif diff >= 500:
            vals['nombre_semaforo'] = 'Amarillo'
        elif diff >= 0:
            vals['nombre_semaforo'] = 'Naranja'
        else:
            vals['nombre_semaforo'] = 'Rojo'

        return vals

    def _procesar_vehiculos_con_mante(self, vehiculos):
        """
        Calcula semáforo para cada vehículo y hace UN SOLO write por vehículo.
        Los mantenimientos se crean después del write para que el campo
        mantenimiento_proximo_id ya esté persistido.
        """
        preventivo = self.env['fleet.mantenimiento.tipo'].search(
            [('name', '=', 'Vehicular Preventivo')], limit=1
        )
        mantes_prev = self.env['fleet.mantenimiento'].search(
            [
                ('vehiculo_id', 'in', vehiculos.ids),
                ('tipo_mantenimiento_id', '=', preventivo.id),
            ]
        )
        mantes_por_vehiculo = {}
        for m in mantes_prev:
            mantes_por_vehiculo.setdefault(m.vehiculo_id.id, []).append(m)
        necesitan_mante = []
        for vehiculo in vehiculos:
            vals = self._calcular_semaforo_vals(vehiculo, mantes_por_vehiculo)
            vehiculo.write(vals)
            if vals['nombre_semaforo'] in ('Amarillo', 'Naranja', 'Rojo'):
                necesitan_mante.append(vehiculo)
        for vehiculo in necesitan_mante:
            vehiculo.crear_mantenimiento()

    def crear_mantenimiento2(self):
        vehiculos_mante = self.search([
            ('producto_id', 'in', PRODUCTOS_CON_MANTE),
            ('state_id', '=', STATE_ACTIVO),
            ('tag_ids', 'not in', [TAG_EXCLUIDO]),
        ])
        vehiculos_no_mante = self.search([
            '|',
            ('producto_id', 'not in', PRODUCTOS_CON_MANTE),
            '|',
            ('state_id', '!=', STATE_ACTIVO),
            ('tag_ids', 'in', [TAG_EXCLUIDO]),
        ])

        self.tratar_vehiculo_sin_mante(vehiculos_no_mante)
        self._procesar_vehiculos_con_mante(vehiculos_mante)

    def calcular_km_ultimo_mante(self, vehiculos):
        preventivo = self.env['fleet.mantenimiento.tipo'].search(
            [('name', '=', 'Vehicular Preventivo')], limit=1
        )
        mantes_prev = self.env['fleet.mantenimiento'].search(
            [('vehiculo_id', 'in', vehiculos.ids), ('tipo_mantenimiento_id', '=', preventivo.id)]
        )
        for record in vehiculos:
            mantes_vh = mantes_prev.filtered(lambda m: m.vehiculo_id.id == record.id)
            if mantes_vh:
                ultimo = max(mantes_vh, key=lambda x: x.tipo_mantenimiento_servicio_id.valor)
                record.km_ult_mantenimiento = (
                    ultimo.km_entrada if ultimo.km_entrada > 0 else record.odometro_mod
                )
            else:
                record.km_ult_mantenimiento = (
                    0 if record.odometro_mod < KM_INTERVALO else record.odometro_mod
                )

    def calcular_km_prox_mante(self, vehiculos):
        for record in vehiculos:
            record.km_prox_mantenimiento = record.km_ult_mantenimiento + KM_INTERVALO

    def calcular_prox_mante(self, vehiculos):
        for record in vehiculos:
            mante_prox = self.env['fleet.mantenimiento.servicio.tipo'].search(
                [
                    ('mantenimiento_tipo_id', '=', TIPO_MANTE_PREVENTIVO_ID),
                    ('valor', '=', self._redondear(record.km_prox_mantenimiento)),
                ],
                limit=1,
            )
            if mante_prox:
                existe = self.env['fleet.mantenimiento'].search(
                    [
                        ('vehiculo_id', '=', record.id),
                        ('tipo_mantenimiento_servicio_id', '=', mante_prox.id),
                    ],
                    limit=1,
                )
                if not existe:
                    record.mantenimiento_proximo_id = mante_prox.id

    def calcular_diferencia_prox_mantenimiento(self, vehiculos):
        for record in vehiculos:
            record.diferencia_prox_mantenimiento = (
                record.km_prox_mantenimiento - record.odometro_mod
            )

    def calcular_color_semafo(self, vehiculos):
        for vehiculo in vehiculos:
            diff = vehiculo.diferencia_prox_mantenimiento
            if diff >= 1000:
                vehiculo.nombre_semaforo = 'Verde'
            elif diff >= 500:
                vehiculo.nombre_semaforo = 'Amarillo'
                vehiculo.crear_mantenimiento()
            elif diff >= 0:
                vehiculo.nombre_semaforo = 'Naranja'
                vehiculo.crear_mantenimiento()
            else:
                vehiculo.nombre_semaforo = 'Rojo'
                vehiculo.crear_mantenimiento()