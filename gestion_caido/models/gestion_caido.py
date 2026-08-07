from odoo import fields,models,api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class GestionCaido(models.Model):
    _name = 'gestion.caido'
    _rec_name = 'rec_name'
    _inherit = ['mail.thread','mail.activity.mixin']
    _order = 'id desc'


    estado_id = fields.Many2one(
        string="Estado",
        comodel_name='gestion.caido.estado',
        default=lambda self: self.env['gestion.caido.estado'].search([('name','=','En gestión')])
    )
    etapa_destino_vehiculo_id = fields.Many2one(
        string="Etapa de destino vehiculo",
        comodel_name='fleet.vehicle.state',
    )
    domain = fields.Char(
        string="Domain",
        compute='_compute_domain',
        store=True
    )
    vehiculo_id = fields.Many2one(
        string="Vehículo",
        comodel_name='fleet.vehicle'
    )
    vehiculos_permitidos_ids = fields.Many2many(
        comodel_name='fleet.vehicle',
        string="Vehiculos permitidos",
        compute='_compute_vehiculos_permitidos',
    )
    model_id = fields.Many2one(
        string="Model",
        comodel_name='fleet.vehicle.model',
        compute='_compute_datos_vehículo',
        store=True
    )
    version_id = fields.Many2one(
        string="Version",
        comodel_name='fleet.customer.version',
        compute='_compute_datos_vehículo',
        store=True
    )
    vin_sn = fields.Char(
        string="Vin",
        compute='_compute_datos_vehículo',
        store=True
    )
    plaza_id = fields.Many2one(
        string="Plaza",
        comodel_name='fleet.customer.plaza',
        compute='_compute_datos_vehículo',
        store=True
    )
    producto_id = fields.Many2one(
        string="Producto",
        comodel_name='fleet.customer.producto',
        compute='_compute_datos_vehículo',
        store=True
    )
    flotilla_id = fields.Many2one(
        string="Flotilla",
        comodel_name='fleet.customer.flotilla',
        compute='_compute_datos_vehículo',
        store=True
    )
    #Datos de contrato
    estado = fields.Selection([
        ('futur','Nuevo'),
        ('open','En proceso'),
        ('expired','Vencido'),
        ('closed','Cancelado')
    ])
    contato_id = fields.Many2one(
        comodel_name='fleet.vehicle.log.contract',
        string="Contato",
        compute="_compute_contrato",
        store=True
    )
    cie = fields.Char(
        string="Cie",
        compute="_compute_datos_contrato",
        store=True
    )
    num_contrato = fields.Char(
        string="Num. contrato",
        compute="_compute_datos_contrato",
        store=True
    )
    arrendatario_id = fields.Many2one(
        string="Arrendatario",
        comodel_name='res.partner',
        compute="_compute_datos_contrato",
        store=True
    )
    nombre_arrendatario = fields.Char(
        string='Arrendatario',
        compute="_compute_datos_contrato",
        store=True
    )
    #Datos del cliente
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string="Cliente",
        compute='_compute_cliente',
        store=True
    )
    correo_cliente = fields.Char(
        string="Correo",
        compute='_compute_datos_cliente',
        store=True
    )
    telefono_cliente = fields.Char(
        string="Teléfono",
        compute='_compute_datos_cliente',
        store=True
    )
    active = fields.Boolean(
        string="Activo",
        default=True
    )
    track_ids = fields.One2many(
        string="Seguimiento",
        comodel_name='gestion.caido.track',
        inverse_name='gestion_id',
    )
    rec_name = fields.Char(
        string="Rec name",
        store=True,
        compute='_compute_rec_name',
    )
    #Evidencia posesion
    ultima_ubi_vehiculo = fields.Char(
        string="Ubicación del vehículo"
    )
    cordenadas_posesion = fields.Char(
        string="Localización posesión"
    )
    evidencia_llave_posesion = fields.Binary(
        string="Evidencia llave",
        attachment=True,
    )
    evidencia_tarjeta_posesion = fields.Binary(
        string="Evidencia tarjeta",
        attachment=True,
    )
    #Evidencia recuperación
    ubi_vehiculo_recuperacion = fields.Char(
        string="Ubicación del vehículo"
    )
    cordenadas_recuperacion = fields.Char(
        string="Localización recuperación"
    )
    evidencia_recuperacion_uno = fields.Binary(
        string="Evidencia recuperación"
    )
    evidencia_recuperacion_dos = fields.Binary(
        string="Evidencia recuperación"
    )
    gestion_activa = fields.Char(
        string="Activo",
        compute="_compute_gestion_activa",
        store=True
    )
    #Retención
    fecha_incio_retencion = fields.Datetime(
        string='Fecha de Incio'
    )
    fecha_estimada_retencion = fields.Datetime(
        string='Fecha de Estimada',
    )
    fecha_finalizacion_retencion = fields.Datetime(
        string='Fecha Finalizacion',
    )
    motivo_retencion = fields.Text(
        string='Motivo de retención'
    )
    motivo_cancelacion_id = fields.Many2one(
        comodel_name='gestion.caido.razon.cancel',
        string='Motivo de cancelación'
    )
    #visualizacion
    mostrar_btn_retencion = fields.Boolean(
        string='Mostrar btn retención',
        default=True
    )
    mostrar_btn_lib_retencion = fields.Boolean(
        string='Mostrar btn lib retención',
        default=True
    )
    mostrar_btn_cambio_etapa = fields.Boolean(
        string='Mostrar btn cambio etapa',
        default=False
    )
    mostrar_page_retencion = fields.Boolean(
        string='Mostrar page retencion',
        default=True
    )
    mostrar_page_posesion = fields.Boolean(
        string='Mostrar page posesion',
        default=True
    )
    mante_ligado_id = fields.Many2one(
        comodel_name='fleet.mantenimiento',
        string='Mantenimiento',
    )
    #gestor
    gestor_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Gestor',
    )
    token_access = fields.Char(
        string="Token de gestor",
    )
    gestores_permitidos = fields.Many2many(
        string="Gestores permitidos",
        comodel_name="hr.employee",
        compute="_compute_gestores_permitidos",
    )

    @api.depends('vehiculo_id')
    def _compute_gestores_permitidos(self):
        gestores = self.env['gestion.caido.gestor'].search([])
        for record in self:
            if record.vehiculo_id:
                plaza_id = record.vehiculo_id.plaza_id.id
                gestores_new = gestores.filtered(lambda g: g.plaza_id.id == plaza_id)
                if gestores_new:
                    gestores_ids = [g.hr_employee_id.id for g in gestores_new]
                    record.gestores_permitidos = gestores_ids
            else:
                record.gestores_permitidos = False

    @api.depends('estado_id')
    def _compute_gestion_activa(self):
        for gestion in self:
            if gestion.estado_id.name == 'Finalizado':
                gestion.gestion_activa = 'Inactiva'
            else:
                gestion.gestion_activa = 'Activa'

    def retener(self):
        self.mostrar_btn_cambio_etapa = True
        self.mostrar_btn_retencion = True
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'gc.retencion',
            'name': 'Retención',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('gestion_caido.gc_retencion_view_form').id,
            'context': {'default_gestion_id': self.id}
        }

    def liberar_retencion(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'gc.liberar.retencion',
            'name': 'Liberar retención',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('gestion_caido.gc_liberar_retencion_view_form').id,
            'context': {'default_gestion_id': self.id}
        }

    @api.depends('estado_id')
    def _compute_domain(self):
        etapas = ['En gestión', 'En posesión', 'Recuperado', 'Finalizado']
        for record in self:
            if record.estado_id.name in etapas:
                record.domain = '[("sequence", "<=", 4)]'
            else:
                record.domain = '[("sequence", "=", 5)]'


    def cambiar_etapa(self):
        self.ensure_one()
        etapa_act = self.estado_id.sequence
        new_stage = self.env['gestion.caido.estado'].search([('sequence','=', etapa_act+1)], limit=1)
        if new_stage.name == 'En posesión':
            return {
                'type': 'ir.actions.client',
                'tag': 'gc_posesion_posesion',
                'name': 'Recepción de Vehículo',
                'target': 'new',
                'context': {
                    'active_id': self.id or (self.ids[0] if self.ids else False),
                    'active_model': self._name,
                    'new_stage': new_stage.id,
                    'vehiculo_id': self.vehiculo_id.id,
                    'type': 'posesion',
                }
            }
        elif new_stage.name == 'Recuperado':
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'gc.liberar.retencion',
                'name': 'Liberar',
                'view_mode': 'form',
                'target': 'new',
                'view_id': self.env.ref('gestion_caido.gc_liberar_retencion_view_form').id,
                'context': {'default_gestion_id': self.id, 'default_type': "no_retencio"}
            }

    def registrar_evento(self,mensaje, fecha_fin=False):
        evento_track = self.env['gestion.caido.track']
        self.ensure_one()
        ultimo_ev = evento_track.search([('gestion_id','=', self.id)], limit=1, order='id desc')
        vals = {
            'gestion_id': self.id,
            'fecha_inicio': fields.Datetime.now(),
            'evento': mensaje
        }
        if fecha_fin:
            vals['fecha_finalizacion'] = fields.Datetime.now()
        new = self.env['gestion.caido.track'].create(vals)
        if ultimo_ev:
            ultimo_ev.fecha_finalizacion = fields.Datetime.now()


    def send_mail(self, res_id, name_template, email="jlimonmunguia@gmail.com"):
        odoo_bot = self.env['res.users'].sudo().browse(1)
        template = self.env.ref(name_template)
        template.with_user(odoo_bot).send_mail(
            res_id,
            force_send=True,
            email_values={
                'email_to': email
            }
        )
        _logger.info("Correo encolado / enviado exitosamente.")

    def obtener_ultima_ubi(self):
        ultima_ubicacon = self.vehiculo_id.ubicacion
        return ultima_ubicacon

    @api.depends('vehiculo_id')
    def _compute_contrato(self):
        for gestion in self:
            contrato = self.env['fleet.vehicle.log.contract'].search([('vehicle_id','=', gestion.vehiculo_id.id)], limit=1, order='id desc').id
            if contrato:
                gestion.contato_id = contrato
            else:
                gestion.contato_id = False

    @api.depends('vehiculo_id')
    def _compute_cliente(self):
        for gestion in self:
            if gestion.vehiculo_id:
                gestion.cliente_id = gestion.vehiculo_id.driver_id
            else:
                gestion.cliente_id = False

    @api.depends('contato_id')
    def _compute_datos_contrato(self):
        for gestion in self:
            if gestion.contato_id:
                gestion.cie = gestion.contato_id.cie
                gestion.num_contrato = gestion.contato_id.ins_ref
                gestion.arrendatario_id = gestion.contato_id.cliente_id
                gestion.estado = gestion.contato_id.state
                gestion.nombre_arrendatario = gestion.contato_id.nombre_cliente
            else:
                gestion.cie = False
                gestion.num_contrato = False
                gestion.arrendatario_id = False
                gestion.estado = False
                gestion.nombre_arrendatario = False

    @api.depends('cliente_id')
    def _compute_datos_cliente(self):
        for gestion in self:
            if gestion.cliente_id:
                gestion.correo_cliente = gestion.cliente_id.email
                gestion.telefono_cliente = gestion.cliente_id.phone
            else:
                gestion.correo_cliente = False
                gestion.telefono_cliente = False

    def _compute_vehiculos_permitidos(self):
        etapa_rentado_id = self.env['fleet.vehicle.state'].search([('es_etapa_rentado', '=', True)], limit=1).id
        flotilla_id = self.env['fleet.customer.flotilla'].search([('name', '=', 'Arrendamiento Pilotea')], limit=1).id
        vehiculos = self.env['fleet.vehicle'].search([
            ('state_id', '=', etapa_rentado_id),
            ('flotilla_id', '=', flotilla_id)
        ]).ids
        self.vehiculos_permitidos_ids = vehiculos

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        tag_gestion = self.env['fleet.vehicle.tag'].search([('name', '=', 'Gestión')], limit=1)
        gestores = self.env['gestion.caido.gestor'].search([])
        gestores_map = {
            g.hr_employee_id.id:g.token_acces for g in gestores
        }
        for gestion in records:
            gestor_token = gestores_map.get(gestion.gestor_id.id)
            if gestor_token == gestion.token_access:
                gestion.vehiculo_id.write({'tag_ids': [(4, tag_gestion.id)], 'edit_vehicle': False})
                self.env['gestion.caido.track'].create({
                    'gestion_id': gestion.id,
                    'fecha_inicio': fields.Datetime.now(),
                    'evento': "Inicia proceso gestión"
                })
            else:
                raise ValidationError("El token del gestor no es valido")
        return records

    def ejecutar_actualizacion_ubicaciones(self):
        cron = self.env.ref(
            "fleet_tecnocontrol.ir_cron_asignar_estado_bloqueo"
        )
        cron.method_direct_trigger()
        return True

    def termino_gestion(self):
        mante_rehabi = self.env['fleet.mantenimiento.tipo'].search([('name', '=', 'Vehicular Rehabilitación')],limit=1).id
        etapa_reacondicionamiento = self.env['fleet.vehicle.state'].search([('name', '=', 'Reacondicionamiento')],limit=1).id
        for record in self:
            record.registrar_evento("Se concluye proceso de gestión", fecha_fin=True)
            record.vehiculo_id.with_context(from_wizard=True).write({
                'btn_confirmar_recepcion': True,
                'tag_ids': [(6, 0, [])],
                'state_id': record.etapa_destino_vehiculo_id.id,
                'edit_vehicle': True
            })
            if record.etapa_destino_vehiculo_id.id == etapa_reacondicionamiento:
                new_mante = self.env['fleet.mantenimiento'].create({
                    'vehiculo_id': record.vehiculo_id.id,
                    'tipo_mantenimiento_id': mante_rehabi,
                    'origen_id': 1
                })
                record.mante_ligado_id = new_mante.id
                record.registrar_evento(f"Se liga mantenimiento: {new_mante.id}")

    @api.depends('vehiculo_id')
    def _compute_datos_vehículo(self):
        for record in self:
            if record.vehiculo_id:
                record.model_id = record.vehiculo_id.model_id
                record.version_id = record.vehiculo_id.version
                record.vin_sn = record.vehiculo_id.vin_sn
                record.plaza_id = record.vehiculo_id.plaza_id
                record.producto_id = record.vehiculo_id.producto_id
                record.flotilla_id = record.vehiculo_id.flotilla_id
            else:
                record.plaza_id = False
                record.version_id = False
                record.vin_sn = False
                record.plaza_id = False
                record.producto_id = False
                record.flotilla_id = False


    @api.depends('vehiculo_id')
    def _compute_rec_name(self):
        for record in self:
            if record.vehiculo_id:
                record.rec_name = f"G-{record.id} / {record.vin_sn}-{record.plaza_id.name}"
            else:
                record.rec_name = f"G-{record.id}"

    def confirmacion_recepcion_cron(self):
        estado_recuperado = self.env['gestion.caido.estado'].search([('name','=', 'Recuperado')])
        estado_finalizado = self.env['gestion.caido.estado'].search([('name', '=', 'Finalizado')])
        gestiones = self.search([('estado_id','=', estado_recuperado.id)])
        for gestion in gestiones:
            _logger.info("==================GEstion x gestion================")
            ultimo_track = self.env['gestion.caido.track'].search([('gestion_id','=', gestion.id)], limit=1, order='id desc')
            _logger.info(ultimo_track)
            _logger.info(ultimo_track.evento)
            if ultimo_track.evento == "Esperando confirmación automática o manual":
                _logger.info("Entra a la validación")
                fecha_limite = ultimo_track.fecha_inicio + timedelta(days=1)
                if fecha_limite < datetime.now():
                    gestion.registrar_evento("Confirmación por Odoo Bot")
                    gestion.termino_gestion()
                    gestion.estado_id = estado_finalizado.id
