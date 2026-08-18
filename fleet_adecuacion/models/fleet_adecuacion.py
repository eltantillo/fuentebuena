from odoo import models, fields, api
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class fleet_adecuacion(models.Model):
    _name = 'fleet.adecuacion'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'rec_name'
    _description = 'Adecuaciones de vehiculos'
    _order = 'id desc'

    "Informacion general"
    adecuacion_id  = fields.Many2one(
        comodel_name='fleet.adecuacion.catalogo',
        string='Tipo de adecuación',
        tracking=True
    )
    fecha_instalacion = fields.Date(
        string='Fecha de instalación',
        tracking=True
    )
    num_serie = fields.Char(
        string='N° de serie',
        tracking=True
    )
    imei = fields.Char(
        string='IMEI',
        tracking=True
    )
    marca = fields.Char(
        string='Marca',
    )
    modelo = fields.Char(
        string='Modelo',
    )
    proveedor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Proveedor',
        domain=[('supplier_rank', '>', 0)]
    )
    "Importe"
    instalacion_incluida = fields.Boolean(
        string='Instalación incluida',
        tracking=True
    )
    incluido_valor_vehiculo = fields.Boolean(
        string='Incluido en valor del vehículo',
        tracking=True
    )
    importe = fields.Float(
        string='Importe',
        tracking=True
    )
    iva = fields.Float(
        string='IVA',
        compute='_compute_iva',
        tracking=True,
        store=True
    )
    total = fields.Float(
        string='Total',
        compute='_compute_total',
        tracking=True,
        store=True
    )
    total_general = fields.Float(
        string='Total general',
        compute='_compute_total_general',
        tracking=True,
        store=True
    )
    "Infromación del vehiculo"
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
    rec_name = fields.Char(
        string='Recibo',
        compute='_compute_rec_name',
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
    expediente_arch = fields.Binary(
        string='Expediente',
        attachment=True,
        required=True
    )
    expendiente_factura = fields.Binary(
        string='Factura',
        attachment=True,
    )
    expediente_arch_xml = fields.Binary(
        string='XML',
        attachment=True,
    )
    active = fields.Boolean('Active', default=True, tracking=True)
    proveedor_adecuacion = fields.Many2one(
        comodel_name = "proveedor.tipo",
        string="Proveedor de adecuación",
        compute="_compute_proveedor",
    )
    validacion_gps = fields.Boolean(
        string="Validación GPS"
    )
    validacion_gnv = fields.Boolean(
        string="Validación GNV"
    )
    existe_expediente_arch = fields.Boolean(
        string="Existe expediente adecuacion",
        compute="_compute_existe_expediente_arch",
        store=True
    )

    @api.depends('expediente_arch')
    def _compute_existe_expediente_arch(self):
        if not self.ids:
            for record in self:
                record.existe_expediente_arch = False
            return
        self.env.cr.execute("""
            SELECT res_id 
            FROM ir_attachment 
            WHERE res_model = %s AND res_field = 'expediente_arch' AND res_id IN %s
        """, (self._name, tuple(self.ids)))
        ids_con_archivo = {row[0] for row in self.env.cr.fetchall()}
        for record in self:
            record.existe_expediente_arch = record.id in ids_con_archivo

    @api.constrains('importe', 'iva', 'total')
    def _constrains_mayor_cero(self):
        adecuacion_gps = self.env['fleet.adecuacion.catalogo'].search([('name','=', 'GPS')], limit=1)
        adecuacion_gnv = self.env['fleet.adecuacion.catalogo'].search([('name','=', 'GNV')], limit=1)
        for record in self:
            if record.adecuacion_id.id in [adecuacion_gnv.id,adecuacion_gps.id]:
                if record.importe <= 0.0 or record.iva <= 0.0 or record.total <= 0.0:
                    raise ValidationError(
                        "Los montos de 'Importe' y 'Total' deben ser mayores a cero para continuar.\n\n"
                        f"  • Adecuación :  {record.adecuacion_id.name}"
                    )


    @api.onchange('adecuacion_id')
    def _onchange_adecuacion(self):
        adecuacion_gps = self.env['fleet.adecuacion.catalogo'].search([('name','=', 'GPS')], limit=1)
        adecuacion_gnv = self.env['fleet.adecuacion.catalogo'].search([('name','=', 'GNV')], limit=1)
        if self.adecuacion_id.id == adecuacion_gnv.id:
            self.validacion_gnv = True
        elif self.adecuacion_id.id == adecuacion_gps.id:
            self.validacion_gps = True
        else:
            self.validacion_gnv = False
            self.validacion_gps = False


    def _compute_proveedor(self):
        tipo = self.env['proveedor.tipo'].search([('name', '=', 'Adecuaciones')], limit=1)
        self.proveedor_adecuacion = tipo.id

    @api.depends('importe')
    def _compute_iva(self):
        for record in self:
            record.iva = record.importe * 0.16

    @api.depends('importe', 'iva')
    def _compute_total(self):
        for record in self:
            record.total = record.importe + record.iva

    @api.depends('instalacion_importe')
    def _compute_instalacion_iva(self):
        for record in self:
            record.instalacion_iva = record.instalacion_importe * 0.16

    @api.depends('instalacion_importe','instalacion_iva')
    def _compute_instalacion_total(self):
        for record in self:
            record.instalacion_total = record.instalacion_importe + record.instalacion_iva

    @api.depends('instalacion_total','total')
    def _compute_total_general(self):
        for record in self:
            record.total_general = record.total + record.instalacion_total

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

    @api.onchange('adecuacion_id')
    def _onchange_tipo_adecuacion(self):
        config = self.env['fleet.adecuacion.config'].search([('plaza_id','=', self.plaza_id.id),('tipo_adecuacion_id','=', self.adecuacion_id.id)], limit=1)
        if config:
            self.importe = config.importe
            self.proveedor_id = config.proveedor_id.id
        else:
            self.importe = 0
            self.proveedor_id = False

    @api.model
    def create(self, vals):
        res = super(fleet_adecuacion, self).create(vals)
        if 'expediente_arch' in vals and vals['expediente_arch']:
                res.message_post(body='✔️ Se subió un nuevo archivo al expediente.')
        return res

    @api.model
    def write(self, vals):
        if 'expediente_arch' in vals:
            if vals['expediente_arch']:
                self.message_post(body='📂 Se actualizó o subió un nuevo archivo al expediente.')
            else:
                self.message_post(body='🗑️ Se elimino el archivo del expediente.')
        instalacion = vals.get('instalacion_incluida')
        if instalacion:
            vals['instalacion_importe'] = 0
            vals['instalacion_iva'] = 0
            vals['instalacion_total'] = 0
        res = super(fleet_adecuacion, self).write(vals)
        return res


    def write_custom(self, vals):
        res = super(fleet_adecuacion, self).write(vals)
        return res

    @api.model
    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.id}-{record.vin_sn}-{record.adecuacion_id.name}"