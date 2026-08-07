from odoo import fields,models,api
import base64
import re

class Adecuacion(models.TransientModel):
    _name = 'adecuacion'


    "Datos de adecuacion"
    tipo_adecuacion_id = fields.Many2one(
        string='Tipo de Adecuacion',
        comodel_name='fleet.adecuacion.catalogo',
    )
    fecha_instalacion = fields.Date(
        string='Fecha de Instalacion',
    )
    num_serie = fields.Char(
        sting="N° de serie"
    )
    imei = fields.Char(
        sting="IMEI"
    )
    marca = fields.Char(
        string="Marca",
    )
    modelo = fields.Char(
        string="Modelo",
    )
    proveedor_id = fields.Many2one(
        string='Proveedor',
        comodel_name='res.partner',
    )
    "Importes"
    importe = fields.Float(
        string='Importe'
    )
    iva = fields.Float(
        string='IVA',
        compute='_compute_iva',
    )
    total = fields.Float(
        string='Total',
        compute='_compute_total',
    )
    total_general = fields.Float(
        string='Total general',
        compute='_compute_total_general',
    )
    instalacion_incluida = fields.Boolean(
        string='¿Instalación incluida?'
    )
    incluido_valor_vehiculo = fields.Boolean(
        string='Incluido en valor del vehículo',
    )
    "Información del vehículo"
    vehiculo_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehículo',
        tracking=True
    )
    numero_economico = fields.Char(
        string='N° de economico',
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
    "Instalación"
    instalacion_proveedor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Proveedor de instalación',
        domain=[('supplier_rank', '>', 0)]
    )
    instalacion_importe = fields.Float(
        string='Importe',
    )
    instalacion_iva = fields.Float(
        string='IVA',
        compute='_compute_instalacion_iva',
        store=True
    )
    instalacion_total = fields.Float(
        string='Total',
        compute='_compute_instalacion_total',
        store=True
    )
    "Documentos"
    document_xml = fields.Binary(
        string='Factura xml',
    )
    expediente_arch = fields.Binary(
        string='Expediente',
    )
    expediente_pdf = fields.Binary(
        string="Expediente"
    )

    @api.depends('instalacion_importe')
    def _compute_instalacion_iva(self):
        for record in self:
            record.instalacion_iva = record.instalacion_importe * 0.16

    @api.depends('instalacion_importe','instalacion_iva')
    def _compute_instalacion_total(self):
        for record in self:
            record.instalacion_total = record.instalacion_importe + record.instalacion_iva

    @api.depends('vehiculo_id')
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

    @api.onchange('tipo_adecuacion_id')
    def _onchange_tipo_adecuacion(self):
        config = self.env['fleet.adecuacion.config'].search([('plaza_id','=', self.plaza_id.id),('tipo_adecuacion_id','=', self.tipo_adecuacion_id.id)], limit=1)
        if config:
            self.importe = config.importe
            self.proveedor_id = config.proveedor_id.id
        else:
            self.importe = 0
            self.proveedor_id = False


    @api.depends('importe')
    def _compute_iva(self):
        for record in self:
            record.iva = record.importe * 0.16

    @api.depends('importe', 'iva')
    def _compute_total(self):
        for record in self:
            record.total = record.importe + record.iva

    def buscar_tipo(self, descripcion):
        tipos = {
            'GAS': 1,
            'Rastreo': 2
        }
        for tipo,valor in tipos.items():
            patron = rf'\b{tipo}\b'
            if re.search(patron, descripcion, re.IGNORECASE):
                return valor
        return False

    @api.depends('total')
    def _compute_total_general(self):
        for record in self:
            record.total_general = record.total

    @api.onchange('document_xml')
    def _onchange_document_xml(self):
        self.importe = False
        self.tipo_adecuacion_id = False
        self.fecha_instalacion = False
        if not self.document_xml:
            return
        xml_bytes = base64.b64decode(self.document_xml)
        data = self.env['xml.parse'].crear_desde_cfdi(xml_bytes)
        descripcion = (data.get('Descripcion') or '').upper()
        adecuacion = self.buscar_tipo(descripcion)
        self.importe = data['subtotal']
        self.tipo_adecuacion_id = adecuacion

    def insertar_adecuacion(self):
        self.env['fleet.adecuacion'].create({
            'adecuacion_id': self.tipo_adecuacion_id.id,
            'fecha_instalacion': self.fecha_instalacion,
            'num_serie': self.num_serie,
            'imei': self.imei,
            'marca': self.marca,
            'modelo': self.modelo,
            'proveedor_id': self.proveedor_id.id,
            'importe': self.importe,
            'instalacion_incluida':self.instalacion_incluida,
            'incluido_valor_vehiculo': self.incluido_valor_vehiculo,
            'instalacion_proveedor_id':self.instalacion_proveedor_id.id,
            'instalacion_importe': self.instalacion_importe,
            'instalacion_iva': self.instalacion_iva,
            'instalacion_total': self.instalacion_total,
            'vehiculo_id': self.vehiculo_id.id,
            'expediente_arch': self.expediente_pdf,
        })
