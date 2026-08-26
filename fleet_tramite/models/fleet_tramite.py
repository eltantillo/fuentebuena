from odoo import models, fields, api
from odoo.exceptions import ValidationError

import logging


_logger = logging.getLogger(__name__)


class FleetTramite(models.Model):
    _name = 'fleet.tramite'
    _rec_name = 'rec_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Fleet Tramite'
    _order = 'id desc'

    "Información"
    tipo_tramite_id = fields.Many2one(
        comodel_name='fleet.tramite.tipo',
        string='Tipo de tramite',
        tracking=True
    )
    folio = fields.Char(
        string='Folio',
        tracking=True
    )
    fecha_tramite = fields.Date(
        string='Fecha tramite',
        tracking=True
    )
    fecha_vencimiento_renovacion = fields.Date(
        string='Fecha vencimiento renovacion',
        tracking=True
    )
    dependencia = fields.Char(
        string='Dependencia',
    )
    estado = fields.Many2one(
        comodel_name='res.country.state',
        string='Estado',
        domain=[('country_id', '=', 'MX')],
    )
    motivo_pago_id = fields.Many2one(
        comodel_name='fleet.tramite.motivo.pago',
        string='Motivo de pago',
    )
    rec_name = fields.Char(
        string='Rec Name',
        compute='_compute_rec_name',
    )
    "Pago"
    importe = fields.Float(
        string='Importe',
        tracking=True,
    )
    aplica_iva = fields.Boolean(
        string='¿Aplica IVA?',
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
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        compute='_compute_datos_vehiculo',
        store=True
    )
    "Observaciones"
    observacion = fields.Text(
        string='Observaciones',
    )
    "Adjuntos"
    expediente = fields.Binary(
        string='Expediente',
        attachment=True,
    )
    expediente_factura = fields.Binary(
        string='Factura',
    )
    expediente_xml = fields.Binary(
        string='Expediente XML',
    )
    active = fields.Boolean('Active', default=True, tracking=True)
    validacion_tarjeta_c = fields.Boolean(
        string='Validación tarjeta ciculación',
    )
    validacion_emplacamiento = fields.Boolean(
        string="Validación emplacamiento"
    )
    existe_expediente = fields.Boolean(
        string="Existe expediente tramite",
        compute="_compute_existe_expediente",
        store=True
    )
    estado_vigencia = fields.Selection(
        selection=[
            ('vigente', 'Vigente'),
            ('vencido', 'Vencido'),
            ('falta_subir', 'Falta subir'),
        ],
        string='Estado',
        compute='_compute_estado_vigencia',
        store=True,
    )

    @api.depends('existe_expediente', 'fecha_vencimiento_renovacion', 'tipo_tramite_id.notificar_renovacion')
    def _compute_estado_vigencia(self):
        today = fields.Date.today()
        for record in self:
            if not record.existe_expediente:
                record.estado_vigencia = 'falta_subir'
            elif record.tipo_tramite_id.notificar_renovacion and (
                not record.fecha_vencimiento_renovacion or record.fecha_vencimiento_renovacion < today
            ):
                record.estado_vigencia = 'vencido'
            else:
                record.estado_vigencia = 'vigente'

    @api.depends('expediente')
    def _compute_existe_expediente(self):
        if not self.ids:
            for record in self:
                record.existe_expediente = False
            return
        self.env.cr.execute("""
            SELECT res_id 
            FROM ir_attachment 
            WHERE res_model = %s AND res_field = 'expediente' AND res_id IN %s
        """, (self._name, tuple(self.ids)))
        ids_con_archivo = {row[0] for row in self.env.cr.fetchall()}
        for record in self:
            record.existe_expediente = record.id in ids_con_archivo

    @api.constrains('importe','total')
    def _constrains_mayor_cero(self):
        emplacamiento = self.env['fleet.tramite.tipo'].search([('name','=','Emplacamiento')], limit=1)
        for record in self:
            if record.tipo_tramite_id.id in [emplacamiento.id]:
                if record.importe <= 0.0 or record.total <= 0.0:
                    raise ValidationError(
                        "Los montos de 'Importe' y 'Total' deben ser mayores a cero para continuar.\n\n"
                        f"  • Trámite :  {record.tipo_tramite_id.name}\n"
                        f"  • Folio   :  {record.folio or 'Sin Folio'}"
                    )

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



    def write(self, vals):
        res = super(FleetTramite, self).write(vals)
        if not self.env.context.get('desde_write_custom'):
            if 'expediente' in vals:
                if vals['expediente']:
                    self.message_post(body='📂 Se actualizó o subió un nuevo archivo al expediente.')
                else:
                    self.message_post(body='🗑️ Se eliminó el archivo del expediente.')
        return res

    def write_custom(self, vals):
        res = super(FleetTramite, self).sudo().with_context(desde_write_custom=True).write(vals)
        if 'expediente' in vals:
            if vals['expediente']:
                self.message_post(body='📂 Se actualizó o subió un nuevo archivo al expediente.')
            else:
                self.message_post(body='🗑️ Se eliminó el archivo del expediente.')
        return res

    @api.model_create_multi
    def create(self, vals_list):
        tarjeta_circulacion = self.env['fleet.tramite.tipo'].search([('name','=','Tarjeta de circulación')], limit=1)
        emplacamiento = self.env['fleet.tramite.tipo'].search([('name','=','Emplacamiento')], limit=1)
        for vals in vals_list:
            _logger.info(f"Create vals expediente: {bool(vals.get('expediente'))}")
            # if vals.get('tipo_tramite_id') in [tarjeta_circulacion.id, emplacamiento.id]:
            #     if not vals.get('expediente'):
            #         raise ValidationError("Se requiere subir el expediente para Tarjeta de circulación o emplacamiento")
        return super().create(vals_list)

    @api.depends('aplica_iva', 'importe')
    def _compute_iva(self):
        for record in self:
            if record.aplica_iva:
                record.iva = record.importe * 0.16
            else:
                record.iva = 0.0

    @api.depends('importe', 'iva')
    def _compute_total(self):
        for record in self:
            if record.aplica_iva:
                record.total = record.importe + record.iva
            else:
                record.total = record.importe

    @api.onchange('tipo_tramite_id')
    def _onchange_validator_tipo_tramite_id(self):
        tarjeta_circulacion = self.env['fleet.tramite.tipo'].search([('name','=','Tarjeta de circulación')], limit=1)
        emplacamiento = self.env['fleet.tramite.tipo'].search([('name','=','Emplacamiento')], limit=1)
        if self.tipo_tramite_id.id == tarjeta_circulacion.id:
            self.validacion_tarjeta_c = True
        elif self.tipo_tramite_id.id == emplacamiento.id:
            self.validacion_emplacamiento = True
        else:
            self.validacion_emplacamiento = False
            self.validacion_tarjeta_c = False



    @api.model
    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.id}-{record.vin_sn}-{record.tipo_tramite_id.name}"

