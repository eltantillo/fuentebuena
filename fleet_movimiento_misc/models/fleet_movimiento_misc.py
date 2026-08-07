from odoo import fields, models, api


class FleetMovimientoMisc(models.Model):
    _name = 'fleet.movimiento.misc'
    _description = 'Movimiento Misc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'rec_name'
    _order = 'id desc'

    etapa_id = fields.Many2one(
        comodel_name='fleet.movimiento.misc.etapa',
        string='Etapa',
    )
    "Datos del movimiento"
    fecha_registro = fields.Datetime(
        string='Fecha de registro',
        default=fields.Datetime.now,
    )
    fecha_movimiento = fields.Date(
        string='Fecha de movimiento',
    )
    tipo_movimiento_id = fields.Many2one(
        comodel_name='fleet.movimiento.misc.tipo',
        string='Tipo de movimiento',
    )
    folio = fields.Char(
        string='Folio',
    )
    folio_factura = fields.Char(
        string='Folio factura',
    )
    estado_id = fields.Many2one(
        comodel_name='res.country.state',
        string='Estado',
        domain=[('country_id', '=', 'MX')],
    )
    municipio_id = fields.Many2one(
        comodel_name='municipio',
        string='Municipio',
    )
    estado_code = fields.Char(
        string='Estado code',
        compute='_compute_estado_code',
    )
    "Datos del proveedor"
    proveedor_id = fields.Many2one(
        comodel_name='res.partner',
        domain=[('supplier_rank', '>', 0)],
        string='Proveedor',
    )
    proveedor_telefono = fields.Char(
        string='Tel. Proveedor',
    )
    motivo_id = fields.Many2one(
        comodel_name='fleet.movimiento.misc.motivo',
        string='Motivo',
    )
    descripcion = fields.Text(
        string='Descipción',
    )
    conductor = fields.Char(
        string='Conductor',
    )
    fecha_vencimiento = fields.Date(
        string='Fecha de vencimiento',
    )
    "Datos del vehículo"
    vehiculo_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehículo',
    )
    numero_economico = fields.Char(
        string='Número economico',
        compute="_compute_datos_vehiculo",
        store=True
    )
    vin_sn = fields.Char(
        string='VIN',
        compute="_compute_datos_vehiculo",
        store=True
    )
    producto_id = fields.Many2one(
        comodel_name='fleet.customer.producto',
        string='Producto',
        compute="_compute_datos_vehiculo",
        store=True
    )
    plaza_id = fields.Many2one(
        comodel_name='fleet.customer.plaza',
        string='Plaza',
        compute="_compute_datos_vehiculo",
        store=True
    )
    matricula = fields.Char(
        string='Matricula',
        compute="_compute_datos_vehiculo",
        store=True
    )
    "Contrato"
    contrato_id = fields.Many2one(
        string='Contrato',
        comodel_name='fleet.vehicle.log.contract',
    )
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
    )
    arrendatario_name = fields.Char(
        string='Arrendatario',
        compute='_compute_arrendatario_name'
    )
    "Importes"
    importe = fields.Float(
        string='Importe',
    )
    aplica_iva = fields.Boolean(
        string='Aplica IVA',
    )
    iva = fields.Float(
        string='IVA',
        compute='_compute_iva',
        store=True,
    )
    total = fields.Float(
        string='Total',
        compute='_compute_total',
        store=True,
    )
    "Pagos"
    importe_pendiente = fields.Float(
        string='Importe pendiente',
        compute='_compute_importe_pendiente',
        store=True,
    )
    importe_pagado = fields.Float(
        string='Importe pagado',
        default=0,
    )
    fecha_ultimo_pago = fields.Date(
        string='Fecha de último pago',
    )
    "Expediente"
    attach_movimiento = fields.Binary(
        string='Expediente',
        attachment=True,
    )
    rec_name = fields.Char(
        string='Referencia',
        compute='_compute_rec_name',
    )
    active = fields.Boolean('Active', default=True, tracking=True)

    @api.depends('contrato_id')
    def _compute_arrendatario_name(self):
        for record in self:
            record.arrendatario_name = record.contrato_id.nombre_cliente

    @api.model
    def create(self, vals):
        res = super(FleetMovimientoMisc, self).create(vals)
        if 'attach_movimiento' in vals and vals['attach_movimiento']:
                res.message_post(body='✔️ Se subió un nuevo archivo al expediente.')
        return res

    @api.model
    def write(self, vals):
        if 'attach_movimiento' in vals:
            if vals['attach_movimiento']:
                self.message_post(body='📂 Se actualizó o subió un nuevo archivo al expediente.')
            else:
                self.message_post(body='🗑️ Se elimino el archivo del expediente.')
        res = super(FleetMovimientoMisc, self).write(vals)
        return res

    def write_custom(self, vals):
        res = super(FleetMovimientoMisc, self).write(vals)
        return res

    @api.depends('aplica_iva','importe')
    def _compute_iva(self):
        for record in self:
            if record.aplica_iva:
                record.iva = record.importe * 0.16
            else:
                record.iva = 0.0

    @api.depends('importe', 'iva')
    def _compute_total(self):
        for record in self:
            record.total = record.importe + record.iva

    @api.depends('total', 'importe_pagado')
    def _compute_importe_pendiente(self):
        for record in self:
            record.importe_pendiente = record.total - record.importe_pagado

    def action_pago(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pagos',
            'res_model': 'fleet.movimiento.pago',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('fleet_movimiento_misc.fleet_movimiento_pago_view_form').id,
            'context': {'default_movimiento_id': self.id}
        }

    @api.depends('vin_sn', 'tipo_movimiento_id')
    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.id}-{record.vin_sn}-{record.tipo_movimiento_id.name}"

    @api.depends('estado_id')
    def _compute_estado_code(self):
        for record in self:
            record.estado_code = record.estado_id.code

    @api.depends('vehiculo_id.vin_sn',
                 'vehiculo_id.numero_economico',
                 'vehiculo_id.producto_id',
                 'vehiculo_id.plaza_id',
                 'vehiculo_id.license_plate')
    def _compute_datos_vehiculo(self):
        for record in self:
            vehiculo = record.vehiculo_id
            if vehiculo:
                record.vin_sn = vehiculo.vin_sn
                record.numero_economico = vehiculo.numero_economico
                record.producto_id = vehiculo.producto_id.id
                record.plaza_id = vehiculo.plaza_id.id
                record.matricula = vehiculo.license_plate
            else:
                record.vin_sn = False
                record.numero_economico = False
                record.producto_id = False
                record.plaza_id = False
