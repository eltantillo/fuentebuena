from odoo import  fields,models,api

class GastoOperativo(models.Model):
    _name = 'gasto.operativo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Motivo',
        compute='_compute_name',
    )
    motivo_id = fields.Many2one(
        comodel_name='gasto.operativo.motivo',
        string='Motivo',
    )
    motivo_name = fields.Char(
        string='Motivo',
        compute='_compute_motivo_name',
    )
    concepto_id = fields.Many2one(
        comodel_name='gasto.operativo.concepto',
        string='Concepto',
    )
    "Información del vehiculo"
    vehiculo_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehiculo',
        tracking=True
    )
    vin_sn = fields.Char(
        string='VIN',
        compute='_compute_datos_vehiculo',
        store=True
    )
    numero_economico = fields.Char(
        string='N° Economico',
        compute='_compute_datos_vehiculo',
        store=True,
    )
    producto_id = fields.Many2one(
        comodel_name='fleet.customer.producto',
        string='Producto',
        compute='_compute_datos_vehiculo',
        store=True
    )
    plaza_id = fields.Many2one(
        comodel_name='fleet.customer.plaza',
        string='Plaza',
        compute='_compute_datos_vehiculo',
        store=True
    )
    agente_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Agente',
    )
    fecha = fields.Date(
        string='Fecha',
    )
    metodo_pago_id = fields.Many2one(
        comodel_name='gasto.operativo.metodo.pago',
        string='Método de Pago',
    )
    es_facturable = fields.Boolean(
        string='¿Es facturable?',
    )
    descripcion = fields.Char(
        string='Descripcion',
    )
    observaciones = fields.Text(
        string='Observaciones',
    )
    "Importes"
    fecha_pago = fields.Date(
        string='Fecha Pago',
    )
    importe = fields.Float(
        string='Importe',
    )
    iva = fields.Float(
        string='IVA',
    )
    total = fields.Float(
        string='Total',
        compute="_compute_total",
        store=True
    )
    attach_gasto_operativo = fields.Binary(
        string='Gasto operativo',
        attachment=True,
    )

    @api.depends('importe','total')
    def _compute_total(self):
        for record in self:
            record.total = record.importe + record.iva

    @api.depends('motivo_id')
    def _compute_motivo_name(self):
        for record in self:
            record.motivo_name = record.motivo_id.name

    @api.depends('vehiculo_id.vin_sn',
                 'vehiculo_id.numero_economico',
                 'vehiculo_id.producto_id',
                 'vehiculo_id.plaza_id')
    def _compute_datos_vehiculo(self):
        for record in self:
            vehiculo = record.vehiculo_id
            if vehiculo:
                record.vin_sn = vehiculo.vin_sn
                record.numero_economico = vehiculo.numero_economico
                record.producto_id = vehiculo.producto_id.id
                record.plaza_id = vehiculo.plaza_id.id
            else:
                record.vin_sn = False
                record.numero_economico = False
                record.producto_id = False
                record.plaza_id = False

    def _compute_name(self):
        for record in self:
            record.name = f"{record.id}-{record.motivo_id.name}"