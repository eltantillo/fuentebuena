from odoo import fields,models,api

class FleetIncidente(models.Model):
    _name = 'fleet.incidente'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string="Nombre",
        compute="_compute_name",
    )
    tipo_incidente_id = fields.Many2one(
        comodel_name="fleet.incidente.tipo",
        string="Tipo de Incidente",
    )
    fecha_inicio = fields.Date(
        string="Fecha Inicio",
    )
    fecha_prevista = fields.Date(
        string="Fecha Prevista",
    )
    fecha_cierre = fields.Date(
        string="Fecha Cierre",
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
    descripcion = fields.Char(
        string="Descripción",
    )
    "Informacion del vehiculo"
    vehiculo_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Vehiculo",
        tracking=True,
    )
    numero_economico = fields.Char(
        string='N° economico',
        compute='_compute_datos_vehiculo',
        store=True
    )
    odometro = fields.Float(
        string='Odometro',
        compute='_compute_datos_vehiculo',
        store=True
    )
    vin_sn = fields.Char(
        string='VIN',
        compute='_compute_datos_vehiculo',
        store=True
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

    def _compute_name(self):
        for record in self:
            record.name = f"{record.id}-{record.vehiculo_id.brand_id.name}/{record.vehiculo_id.model_id.name}/{record.vehiculo_id.license_plate}-{record.tipo_incidente_id.name}"

    @api.depends('vehiculo_id')
    def _compute_datos_vehiculo(self):
        for record in self:
            record.vin_sn = record.vehiculo_id.vin_sn
            record.numero_economico = record.vehiculo_id.numero_economico
            record.producto_id = record.vehiculo_id.producto_id.id
            record.plaza_id = record.vehiculo_id.plaza_id.id
            record.odometro = record.vehiculo_id.odometer


    @api.depends('importe','total')
    def _compute_total(self):
        for record in self:
            record.total = record.importe + record.iva