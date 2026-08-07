from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FleetPoliza(models.Model):
    _name = 'fleet.poliza'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'rec_name'
    _description = 'Polizas de seguro'
    _order = 'id desc'

    "Datos de la poliza"
    tipo_poliza_id = fields.Many2one(
        string='Tipo',
        comodel_name='fleet.poliza.tipo',
    )
    num_poliza = fields.Char(
        string='N° de póliza',
        tracking=True
    )
    proveedor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Proveedor',
        domain=[('supplier_rank', '>', 0)]
    )
    tipo_cobertura_id = fields.Many2one(
        comodel_name='fleet.poliza.tipo.cobertura',
        string='Tipo de cobertura'
    )
    fecha_inicio = fields.Date(
        string='Fecha de inicio',
        tracking=True
    )
    fecha_vencimiento = fields.Date(
        string='Fecha de vencimiento',
        tracking=True
    )
    tipo_valor_id = fields.Many2one(
        comodel_name='fleet.poliza.tipo.valor',
        string='Tipo de valor'
    )
    rec_name = fields.Char(
        string='Rec Name',
        compute='_compute_rec_name',
    )
    "Importes"
    prima_neta = fields.Float(
        string='Prima neta',
        tracking=True
    )
    gasto_expedicion = fields.Float(
        string='Gastos de expedición',
        tracking=True
    )
    iva = fields.Float(
        string='IVA',
        compute='_compute_iva',
        tracking=True,
        store=True
    )
    importe_total = fields.Float(
        string='Importe total',
        compute='_compute_importe_total',
        tracking=True,
        store=True
    )
    "Información del vehículo"
    vehiculo_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehículo',
        tracking=True
    )
    numero_economico = fields.Char(
        string='N° economico',
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
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        compute='_compute_datos_vehiculo',
        store=True
    )
    proveedor_polizas = fields.Many2one(
        comodel_name = "proveedor.tipo",
        string="Proveedor de polizas",
        compute="_compute_proveedor",
    )
    "Documentos"
    attach_poliza = fields.Binary(
        string='Póliza',
        attachment=True,
    )
    attach_factura = fields.Binary(
        string='Factura',
        attachment=True,
    )
    attach_poliza_xml = fields.Binary(
        string='Póliza XML',
        attachment=True,
    )
    active = fields.Boolean('Active', default=True, tracking=True)


    @api.constrains('prima_neta','gasto_expedicion','iva', 'importe_total')
    def _constarint_montos(self):
        tipo_poliza = self.env['fleet.poliza.tipo'].search([('name','=', 'Póliza')])
        for record in self:
            if record.tipo_poliza_id.id == tipo_poliza.id:
                if record.prima_neta <= 0.0 or record.gasto_expedicion <= 0.0 or record.iva <= 0.0 or record.importe_total <= 0.0:
                    raise ValidationError("Los montos de 'prima_neta', 'gasto_expedicion', 'iva' e 'importe_total' deben ser mayores a 0.")

    def _compute_proveedor(self):
        tipo = self.env['proveedor.tipo'].search([('name', '=', 'Pólizas de seguro')], limit=1)
        self.proveedor_polizas = tipo.id

    @api.depends('prima_neta', 'gasto_expedicion')
    def _compute_iva(self):
        for record in self:
            total = record.prima_neta + record.gasto_expedicion
            record.iva =  total * 0.16

    @api.depends('prima_neta','gasto_expedicion','iva')
    def _compute_importe_total(self):
        for record in self:
            record.importe_total = record.prima_neta + record.gasto_expedicion + record.iva

    @api.model
    def create(self, vals):
        res = super(FleetPoliza, self).create(vals)
        if 'attach_poliza' in vals and vals['attach_poliza']:
            res.message_post(body='✔️ Se subió un nuevo archivo al expediente.')
        return res

    @api.model
    def write(self, vals):
        if 'attach_poliza' in vals:
            if vals['attach_poliza']:
                self.message_post(body='📂 Se actualizó o subió un nuevo archivo al expediente.')
            else:
                self.message_post(body='🗑️ Se elimino el archivo del expediente.')
        res = super(FleetPoliza, self).write(vals)
        return res

    def write_custom(self, vals):
        res = super(FleetPoliza, self).write(vals)
        return res

    @api.depends('vehiculo_id.vin_sn',
                 'vehiculo_id.numero_economico',
                 'vehiculo_id.producto_id',
                 'vehiculo_id.plaza_id',
                 'vehiculo_id.driver_id')
    def _compute_datos_vehiculo(self):
        for record in self:
            vehiculo = record.vehiculo_id
            if vehiculo:
                record.vin_sn = vehiculo.vin_sn
                record.numero_economico = vehiculo.numero_economico
                record.producto_id = vehiculo.producto_id.id
                record.plaza_id = vehiculo.plaza_id.id
                record.cliente_id = vehiculo.driver_id.id
            else:
                record.vin_sn = False
                record.numero_economico = False
                record.producto_id = False
                record.plaza_id = False
                record.cliente_id = False

    @api.model
    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.id}-{record.vin_sn}-{record.num_poliza}"