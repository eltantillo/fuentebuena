from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)


class FleetCustomerInheritFleet(models.Model):
    _inherit = 'fleet.vehicle'
    _rec_name = 'rec_name'
    _order = 'create_date desc'

    ultimo_cambio_etapa = fields.Date(
        string='Último cambio de etapa',
        tracking=True
    )
    numero_economico = fields.Char(
        string='Número economico',
        tracking=True
    )
    proveedor_id = fields.Many2one(
        comodel_name='res.partner',
        domain=[('supplier_rank', '>', 0)],
        string='Proveedor',
        tracking=True
    )
    es_gnv = fields.Boolean(
        string='GNV',
        tracking=True
    )
    fecha_puesta_punto = fields.Datetime(
        string='Fecha puesta punto',
        tracking=True
    )
    condicion_vehiculo_id = fields.Many2one(
        comodel_name='fleet.customer.condicion.vehiculo',
        string='Condición del vehículo',
        tracking=True
    )
    uso_vehiculo_id = fields.Many2one(
        comodel_name='fleet.customer.uso.vehiculo',
        string='Uso de vehículo',
        tracking=True
    )
    flotilla_id = fields.Many2one(
        comodel_name='fleet.customer.flotilla',
        string='Flotilla',
        tracking=True
    )
    sub_etapa_id = fields.Many2one(
        comodel_name='fleet.customer.sub.etapa',
        string='Sub etapa',
        default=lambda self: self.env['fleet.customer.sub.etapa'].search([('name','=', 'Alta')], limit=1).id,
        tracking=True
    )
    sub_etapas_ids = fields.Many2many(
        comodel_name='fleet.customer.sub.etapa',
        related='state_id.sub_etapa_ids',
        string='Sub etapas',
    )
    mostrar_sub_etapa = fields.Boolean(
        string='Mostrar sub etapa',
        compute='_compute_mostar_sub_etapa',
    )
    producto_id = fields.Many2one(
        comodel_name='fleet.customer.producto',
        string='Producto',
        tracking=True
    )
    plaza_id = fields.Many2one(
        comodel_name='fleet.customer.plaza',
        string='Plaza',
        tracking=True
    )
    baja = fields.Boolean(
        string='¿Es baja?',
        tracking=True
    )
    motivo_baja_id = fields.Many2one(
        comodel_name='fleet.customer.motivo.baja',
        string='Motivo de baja',
        tracking=True
    )
    fecha_baja  = fields.Date(
        string='Fecha de baja',
        tracking=True
    )
    color_interior = fields.Char(
        string='Color interior',
        tracking=True
    )
    "Adquisición"
    fecha_adquisicion = fields.Date(
        string='Fecha adquisición',
        tracking=True
    )
    condicion_adquisicion_id = fields.Many2one(
        comodel_name='fleet.customer.condicion.vehiculo',
        string='Condición adquisición',
        tracking=True
    )
    "Factura"
    factura = fields.Char(
        string='Factura',
        tracking=True
    )
    fecha_factura = fields.Date(
        string='Fecha factura',
        tracking=True
    )
    folio_uuid = fields.Char(
        string='Folio UUID',
        tracking=True
    )
    fecha_carta_porte = fields.Date(
        string='Fecha carta porte',
        tracking=True
    )
    folio_carta_porte = fields.Char(
        string='Folio carta porte',
        tracking=True
    )
    "Orden de compra"
    fecha_recepcion = fields.Date(
        string='Fecha recepción',
        tracking=True
    )
    orden_compra = fields.Char(
        string='Orden de compra',
        tracking=True
    )
    fecha_orden_compra = fields.Date(
        string='Fecha orden de compra',
        tracking=True
    )
    "Importes de adquisición"
    importe_adquisicion = fields.Float(
        string='Importe adquisición',
        tracking=True
    )
    iva_adquisicion = fields.Float(
        string='IVA adquisición',
        tracking=True
    )
    importe_total_adquisicion = fields.Float(
        string='Importe total adquisición',
        tracking=True
    )
    valor_residual_adquisicion = fields.Float(
        string='Valor residual adquisición',
        tracking=True
    )
    "Documentos"
    factura_vehiculo = fields.Binary(
        string='Factura vehículo',
        attachment=True,
    )
    opcion_compra = fields.Binary(
        string='Opcion compra',
        attachment=True
    )
    "Adicionales"
    odometro_mod = fields.Float(
        string='Odómetro mod'
    )
    rec_name = fields.Char(
        string='Rec name',
        compute='_compute_rec_name',
    )
    "Reacondicionamiento"
    fecha_prox_reacondicionamiento = fields.Date(
        string='Fecha reacondicionamiento',
        tracking=True
    )
    mostrar_fecha_prox_reacond = fields.Boolean(
        string='Mostrar fecha de reacondicionamiento',
        compute='_compute_mostrar_fecha_prox_reacond',
        tracking=True
    )
    mostrar_driver = fields.Boolean(
        string='Mostrar driver',
        compute='_compute_mostrar_driver',
    )
    version = fields.Many2one(
        comodel_name='fleet.customer.version',
        string='Versión',
        tracking=True
    )
    numero_motor = fields.Char(
        string='Número de motor',
        tracking=True
    )
    nombre_modelo = fields.Char(
        string='Nombre del modelo',
        related='model_id.name',
    )
    modelo_factura = fields.Char(
        string='Modelo factura',
        tracking=True
    )
    required_disponible = fields.Boolean(
        string='Required disponible',
    )
    odometer = fields.Float(compute='_asignar_odometro', inverse='_set_odometer', string='Last Odometer',
        help='Odometer measure of the vehicle at the moment of this log')
    tag_ids = fields.Many2many('fleet.vehicle.tag', 'fleet_vehicle_vehicle_tag_rel', 'vehicle_tag_id', 'tag_id', 'Tags', copy=False, tracking=True)
    state_id = fields.Many2one(
        comodel_name= 'fleet.vehicle.state',
        string='State',
        default=lambda self: self.env['fleet.vehicle.state'].search([('name', '=', 'En registro')], limit=1).id,
    )

    def _get_year_selection(self):
        current_year = datetime.now().year
        return [(str(i), i) for i in range(1970, current_year + 2)]

    @api.onchange('state_id')
    def _onchange_state_id(self):
        etapa_disponible = self.env['fleet.vehicle.state'].search([('es_estapa_disponible', '=', True)], limit=1)
        if self.state_id.id == etapa_disponible.id:
            self.required_disponible = True
        else:
            self.required_disponible = False


    def _asignar_odometro(self):
        ModelOdometro = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = ModelOdometro.search([('vehicle_id', '=', record.id)], limit=1, order='create_date desc')
            if vehicle_odometer:
                record.odometer = vehicle_odometer.value
            else:
                record.odometer = 0

    @api.depends('model_id.name', 'vin_sn')
    def _compute_vehicle_name(self):
        for record in self:
            record.name = (record.model_id.name or '') + '/' + (record.vin_sn or '')

    @api.depends('state_id')
    def _compute_mostrar_driver(self):
        for vehiculo in self:
            if not vehiculo.id:
                vehiculo.mostrar_driver = False
            else:
                if vehiculo.sub_etapa_id.name == 'Alta' or vehiculo.sub_etapa_id.name == 'Alta':
                    vehiculo.mostrar_driver = False
                else:
                    vehiculo.mostrar_driver = True

    @api.depends('state_id')
    def _compute_mostrar_fecha_prox_reacond(self):
        for vehiculo in self:
            if vehiculo.state_id.es_etapa_reacondicionamiento:
                vehiculo.mostrar_fecha_prox_reacond = True
            else:
                vehiculo.mostrar_fecha_prox_reacond = False

    @api.depends('state_id')
    def _compute_mostar_sub_etapa(self):
        for vehiculo in self:
            if len(vehiculo.sub_etapas_ids) >= 1:
                vehiculo.mostrar_sub_etapa = True
            else:
                vehiculo.mostrar_sub_etapa = False

    @api.depends('model_id','vin_sn')
    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.model_id.name}/{record.vin_sn}"

    @api.model
    def create(self, vals):
        uso_id = self.env['fleet.customer.uso.vehiculo'].browse(1)
        _logger.info("================= CREATE =================")
        etapa_alta = self.env['fleet.vehicle.state'].search([('name', '=', 'En registro')], limit=1)
        _logger.info(etapa_alta)
        sub_etapa = self.env['fleet.customer.sub.etapa'].search([('name', '=', 'Alta')], limit=1)
        _logger.info(sub_etapa)
        for val in vals:
            val['acquisition_date'] = fields.Date.today()
            if uso_id:
                val['uso_vehiculo_id'] = uso_id.id
            if not val['state_id']:
                val['state_id'] = etapa_alta.id
                val['sub_etapa_id']= sub_etapa.id
        res = super(FleetCustomerInheritFleet, self).create(vals)
        res.calcular_num_economico()
        return res


    @api.model
    def write(self, vals):
        id_rentado = self.env['fleet.vehicle.state'].search([('es_etapa_rentado', '=', True)])
        if 'state_id' in vals:
            state = self.env['fleet.vehicle.state'].search([('id', '=', vals['state_id'])])
            self.fecha_prox_reacondicionamiento = False
            self.sub_etapa_id = False
            if not self.fecha_recepcion and not state.name == 'En registro':
                raise ValidationError('No se puede cambiar de etapa sin fecha de recepción')
            elif self.state_id.id == id_rentado.id and state.es_estapa_disponible:
                raise ValidationError('No se puede cambiar de etapa: Rentado a Disponible')
            elif state.name == 'Rentado':
                self.next_assignation_date = fields.Date.today()
            self.ultimo_cambio_etapa = fields.Date.today()
        res = super(FleetCustomerInheritFleet, self).write(vals)
        return res

    def write_custom(self, vals):
        res = super(FleetCustomerInheritFleet, self).write(vals)
        return res

    @api.constrains('vin_sn')
    def _check_vin_sn(self):
        vin = self.vin_sn
        num_coches = self.search_count([('vin_sn', '=', vin)])
        if num_coches > 1:
            raise ValidationError('No se puede utilizar el mismo VIN para dos o mas vehículos')

    def dar_baja(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Baja de vehiculo',
            'res_model': 'fleet.customer.baja',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('fleet_customer.fleet_customer_baja_view_form').id
        }

    def asigar_opcion_compra(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Asigar opción a compra',
            'res_model': 'fleet.opcion.compra',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('fleet_customer.fleet_opcion_compra_view_form').id
        }

    def calcular_num_economico(self):
        prefijo_modelo = self.model_id.prefijo or ''
        year_modelo = str(self.model_year)[-1]
        prefijo_producto =  self.producto_id.prefijo
        if prefijo_producto == 'P':
            prefijo_producto = ''
        prefijo = prefijo_producto + prefijo_modelo
        registros_similares = self.search([('numero_economico','like', prefijo + '%')])
        nuevo_consecutivo = 1
        consecutivos_excistentes = []
        for registro in registros_similares:
            if registro.numero_economico and len(registro.numero_economico) >= len(prefijo) + 4:
                try:
                    consecutivo = int(registro.numero_economico[-4:])
                    consecutivos_excistentes.append(consecutivo)
                except ValueError:
                    pass
        if consecutivos_excistentes:
            nuevo_consecutivo = max(consecutivos_excistentes) + 1
        consecutivo_str = ('%04d' % nuevo_consecutivo)
        nuevo_id = prefijo + year_modelo + consecutivo_str
        self.write({
            'numero_economico': nuevo_id
        })