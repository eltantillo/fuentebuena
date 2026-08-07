from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class FleetSiniestro(models.Model):
    _name = 'fleet.siniestro'
    _description = 'Siniestro'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'rec_name'
    _order = 'id desc'


    etapa_id = fields.Many2one(
        comodel_name='fleet.siniestro.etapa',
        string='Etapa',
        tracking=True,
    )
    fase_id = fields.Many2one(
        comodel_name='fleet.siniestro.fase',
        string='Fase',
        tracking=True,
    )
    aseguradora_id = fields.Many2one(
        comodel_name='res.partner',
        string='Aseguradora',
    )
    siniestro_tipo_id = fields.Many2one(
        comodel_name='fleet.siniestro.tipo',
        string='Tipo de siniestro',
        tracking=True,
    )
    movilidad_id = fields.Many2one(
        comodel_name='fleet.siniestro.movilidad',
        string='Movilidad',
        tracking=True,
    )
    folio = fields.Char(
        string='Folio',
    )
    siniestro = fields.Char(
        string='Siniestro',
    )
    siniestro_estatus_id = fields.Many2one(
        comodel_name='fleet.siniestro.estatus',
        string='Estatus del siniestro',
        tracking=True,
    )
    fecha_ingreso_valuacion = fields.Date(
        string='Fecha ingreso a valuación',
        tracking=True,
    )
    fecha_ingreso_reparacion = fields.Date(
        string='Fecha ingreso a reparación',
        tracking=True,
    )
    fecha_compromiso_entrega = fields.Date(
        string='Fecha de comprimiso de entrega',
        tracking=True,
    )
    fecha_entrega = fields.Date(
        string='Fecha de entrega',
        tracking=True,
    )
    fecha_cierre = fields.Date(
        string='Fecha de cierre',
        tracking=True,
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
    "Conductor"
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        tracking=True,
    )
    cliente_email = fields.Char(
        string='Email cliente',
    )
    cliente_telefono = fields.Char(
        string='Télefono cliente',
    )
    cliente_nombre = fields.Char(
        string='Nombre cliente',
    )
    "Evento"
    fecha_hora_suceso = fields.Datetime(
        string='Fecha y hora del suceso',
        tracking=True,
    )
    fecha_hora_notifiacion = fields.Date(
        string='Fecha y hora de notificación',
        tracking=True,
    )
    ubicacion = fields.Char(
        string='Ubicación',
        tracking=True,
    )
    conductor = fields.Char(
        string='Conductor',
        tracking=True,
    )
    telefono_conductor = fields.Char(
        string='Telefono conductor',
    )
    descripcion_siniestro = fields.Text(
        string='Descripción del siniestro',
    )
    rec_name = fields.Char(
        string='Nombre',
        compute='_compute_rec_name',
    )
    active = fields.Boolean('Active', default=True, tracking=True)
    proveedor_siniestro = fields.Many2one(
        comodel_name = "proveedor.tipo",
        string="Proveedor de compra de coches",
        compute="_compute_proveedor",
    )
    estado_actual_id = fields.Many2one(
        related='vehiculo_id.state_id',
        string='Estado actual',
        comodel_name='fleet.vehicle.state'
    )
    dictamen = fields.Selection([
        ('afectado','Afectado'),
        ('responsable','Responsable'),
        ('robo','Robo')], string='Dictamen',
    )
    folio_aseguradora = fields.Char(
        string='Folio aseguradora',
    )
    perdida_total = fields.Boolean(
        string='Perdida total',
    )
    #DAtos de afectado
    existe_responsable  = fields.Selection([
        ('si','Si'),
        ('no','No'),],
        string='¿Existe responsable?',
    )
    numero_acta = fields.Char(
        string='Numero acta',
    )
    responsable_seguro = fields.Selection([
        ('si', 'Si'),
        ('no', 'No'), ],
        string="Responsable con seguro"
    )
    aseguradora = fields.Char(
        string='Aseguradora',
    )
    #Datos responsable
    dentro_cobertura = fields.Selection([
        ('si', 'Si'),
        ('no', 'No'), ],
        string='¿Dentro cobertura?'
    )
    deducible = fields.Float(
        string='Deducible',
    )
    unidad_sin_dano = fields.Boolean(
        string='Unidad sin daño',
    )
    taller = fields.Char(
        string='Taller',
    )
    mostrar_boton = fields.Boolean(
        string='Mostrar botón',
        compute='_compute_mostrar_boton',
    )
    mostrar_renta_auxilio = fields.Boolean(
        string='Mostrar renta auxilio',
        compute='_compute_mostrar_renta_auxilio',
    )

    def _compute_mostrar_boton(self):
        for record in self:
            if record.fase_id.name == 'Abierto':
                record.mostrar_boton = False
            else:
                record.mostrar_boton = True

    def _compute_mostrar_renta_auxilio(self):
        fase_abierto = self.env['fleet.siniestro.fase'].search([('name','=','Abierto')])
        for record in self:
            if record.aplica_renta_auxilio:
                record.mostrar_renta_auxilio = True
            else:
                if record.fase_id.id == fase_abierto.id:
                    rentas_aux = self.env['fleet.siniestro.renta.auxilio.track'].search([('vehiculo_siniestro_id','=',record.vehiculo_id.id),('estado','=', 'active')])
                    if rentas_aux:
                        record.mostrar_renta_auxilio = True
                    else:
                        record.mostrar_renta_auxilio = False
                else:
                    record.mostrar_renta_auxilio = True


    def _compute_proveedor(self):
        tipo = self.env['proveedor.tipo'].search([('name', '=', 'Aseguradora')], limit=1)
        self.proveedor_siniestro = tipo.id



    @api.depends('vehiculo_id.vin_sn',
                 'vehiculo_id.numero_economico',
                 'vehiculo_id.producto_id',
                 'vehiculo_id.plaza_id','vehiculo_id.driver_id')
    def _compute_datos_vehiculo(self):
        for record in self:
            vehiculo = record.vehiculo_id
            if vehiculo:
                record.vin_sn = vehiculo.vin_sn
                record.numero_economico = vehiculo.numero_economico
                record.producto_id = vehiculo.producto_id.id
                record.plaza_id = vehiculo.plaza_id.id
                record.cliente_id = vehiculo.driver_id.id
                record.cliente_email = vehiculo.driver_id.email
                record.cliente_telefono = vehiculo.driver_id.phone
                record.conductor = vehiculo.driver_id.name
                record.telefono_conductor = vehiculo.driver_id.phone

            else:
                record.vin_sn = False
                record.numero_economico = False
                record.producto_id = False
                record.plaza_id = False
                record.cliente_id = False
                record.cliente_email = False
                record.cliente_telefono = False
                record.conductor = False
                record.telefono_conductor = False

    @api.depends('vehiculo_id')
    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.id}-{record.folio}-{record.siniestro_tipo_id.name}"

    def write_custom(self, vals):
        res = super(FleetSiniestro, self).write(vals)
        return res

    @api.model
    def update_attachments_datas(self, attachments_data):
        Attachment = self.env['ir.attachment'].sudo()
        for att in attachments_data:
            att_id = att.get('id')
            datas = att.get('datas')
            if not att_id or not datas:
                continue
            attachment = Attachment.browse(att_id)
            if attachment.exists():
                try:
                    attachment.write({
                        'datas': datas
                    })
                    _logger.info(f"✅ Attachment actualizado: {att_id}")
                except Exception as e:
                    _logger.error(f"❌ Error actualizando {att_id}: {e}")
            else:
                _logger.warning(f"⚠️ Attachment no existe en destino: {att_id}")

    def renta_auxilio(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'renta.auxilio',
            'name': 'Renta Auxilio',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('fleet_siniestro.fleet_siniestro_renta_auxilio_form').id,
            'context': {'default_vehiculo_siniestro_id': self.vehiculo_id.id, 'default_cliente_siniestro_id': self.vehiculo_id.driver_id.id,
                        'default_siniestro_id': self.id, 'default_plaza_id': self.plaza_id.id}
        }

    # @api.model
    # def write(self, vals):
    #     estado_revision = self.env['fleet.siniestro.etapa'].search([('name','=', 'Revisión')], limit=1)
    #     estado_gestoria = self.env['fleet.siniestro.etapa'].search([('name', '=', 'Gestoría')], limit=1)
    #     if 'etapa_id' in vals:
    #         state = self.env['fleet.siniestro.etapa'].search([('id', '=', vals['etapa_id'])])
    #         if state.name == 'Revisión' and not self.aseguradora_id and not self.movilidad_id and not  self.siniestro_estatus_id and not self.fecha_compromiso_entrega and not  self.fecha_ingreso_valuacion:
    #             raise ValidationError('Necesita llenar los datos')
    #         elif state.name == 'Gestoría' and not self.fec:
    #             raise ValidationError('Llenar los datos')