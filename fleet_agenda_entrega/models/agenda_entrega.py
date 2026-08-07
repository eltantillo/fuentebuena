from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)

class AgendaEntrega(models.Model):
    _name = 'agenda.entrega'
    _description = 'Agenda Entrega'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'rec_name'
    _order = 'create_date desc'

    etapa_id = fields.Many2one(
        comodel_name='agenda.entrega.etapa',
        string='Etapa',
        default=1,
        tracking=True,
    )
    "Dictamen"
    dictamen_id = fields.Many2one(
        comodel_name='agenda.entrega.dictamen',
        string='Dictamen',
        tracking=True,
    )
    estatus_dictamen = fields.Many2one(
        comodel_name="agenda.entrega.estatus.dictamen",
        string="Estatus de dictamen",
        compute='_compute_datos_dictamen',
        store=True
    )
    email_cliente = fields.Char(
        string="Email"
    )
    telefono_cliente = fields.Char(
        string="Telefono"
    )
    "Solicitud"
    asesor_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Asesor',
        compute='_compute_datos_dictamen',
        store=True
    )
    num_empleado = fields.Char(
        string='Num. Empleado',
        compute='_compute_num_empleado',
        compute_sudo=True,
        store=True
    )
    fecha_entrega = fields.Datetime(
        string='Fecha de entrega',
        tracking=True,
    )
    lugar_entrega_id = fields.Many2one(
        comodel_name='agenda.entrega.lugar',
        string='Lugar de entrega',
        tracking=True,
    )
    indicaciones = fields.Text(
        string='Indicaciones',
        tracking=True,
    )
    canalizacion_id = fields.Many2one(
        comodel_name='agenda.entrega.canalizacion',
        string='Canalizacion'
    )
    "Vehiculo"
    vehiculo_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Vehiculo",
        compute='_compute_datos_vehiculo',
        store=True,
        tracking=True,
    )
    modelo_vehiculo_id = fields.Many2one(
        comodel_name="fleet.vehicle.model",
        string="Modelo",
        compute = '_compute_datos_vehiculo',
        store=True
    )
    version = fields.Many2one(
        comodel_name='fleet.customer.version',
        string='Version',
        compute='_compute_datos_vehiculo',
        store=True
    )
    vin_sn = fields.Char(
        string='VIN',
        compute='_compute_datos_vehiculo',
        store=True
    )
    condicion_vehiculo_id = fields.Many2one(
        comodel_name='fleet.customer.condicion.vehiculo',
        string='Condicion',
        compute='_compute_datos_vehiculo',
        store=True
    )
    color = fields.Char(
        string='Color',
        compute='_compute_datos_vehiculo',
        store=True
    )
    year = fields.Char(
        string='Year',
        compute = '_compute_datos_vehiculo',
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
    "Mesa de control"
    req_instrumentacion = fields.Many2one(
        comodel_name='agenda.entrega.estatus.instru',
        string='Requerimientos de instrumentacion',
        tracking=True
    )
    estatus_comprobante_deposito = fields.Many2one(
        comodel_name='agenda.entrega.estatus.comprobante',
        string='Estatus comprobante depósito',
        tracking=True,
    )
    "Entrega"
    fecha_confirmada = fields.Datetime(
        string='Fecha confirmada',
        tracking=True,
    )
    hora_confirmada = fields.Char(
        string='Hora de confirmación',
        compute="_compute_hora_confirmada"
    )
    ejecutivo_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Ejecutivo',
        compute="_compute_gerente"
    )
    nota = fields.Text(
        string='Nota',
        tracking=True,
    )
    autorizacion_uso = fields.Boolean(
        string='Autorizacion de uso de datos'
    )
    evidencia_autorizacion = fields.Binary(
        string='Evidencia de autorización'
    )
    foto_entrega = fields.Binary(
        string='Foto de entrega',
        attachment=True,
    )
    "Adición"
    contador = fields.Integer(
        string='Contador'
    )
    rec_name = fields.Char(
        string='Rec name',
        compute='_compute_rec_name'
    )
    mostrar_evento = fields.Boolean(
        string='Mostrar evento',
        compute='_compute_mostrar_evento',
    )
    color_kanban = fields.Integer(
        string="Color KanBan",
        compute="_compute_color_kanban"
    )
    active = fields.Boolean('Active', default=True, tracking=True)
    eventos_pendientes = fields.Integer(
        string="Eventos pendientes",
        compute="_compute_eventos"
    )
    eventos_solventados = fields.Integer(
        string="Eventos solventados",
        compute="_compute_eventos"
    )
    instrumentacion_correcta = fields.Boolean(
        string="Instrumentación correcta",
        compute="_compute_instrumentacion_correcta"
    )
    cliente = fields.Char(
        string="Cliente",
        store=True,
        compute="_compute_datos_vehiculo"
    )
    matricula = fields.Char(
        string="Matricula",
        store=True,
        compute="_compute_datos_vehiculo"
    )
    id_landing = fields.Char(
        string="Id Landing",
        compute="_compute_datos_vehiculo",
        store=True
    )
    dictamen_valido_ids = fields.Many2many(
        comodel_name='agenda.entrega.dictamen',
        compute="_compute_dictamen_validos",
        string='Dictamen'
    )


    def _compute_dictamen_validos(self):
        _logger.info("================")
        etapa_solicitado = self.env['agenda.entrega.etapa'].search([('name','=', 'Solicitado')], limit=1)
        _logger.info(f"etapa_solicitado: {etapa_solicitado}")
        etapa_confirmado = self.env['agenda.entrega.etapa'].search([('name','=', 'Confirmado')], limit=1)
        _logger.info(f"etapa_confirmado: {etapa_confirmado}")
        etapa_entregado = self.env['agenda.entrega.etapa'].search([('name','=', 'Entregado')], limit=1)
        _logger.info(f"etapa_confirmado: {etapa_entregado}")
        agendas = self.search([('etapa_id','in',[etapa_solicitado.id, etapa_entregado.id, etapa_confirmado.id])])
        _logger.info(f"agendas count: {len(agendas)}")
        dictamenes_no_validos = agendas.dictamen_id.ids
        _logger.info(f"dictamenes_no_validos: {len(dictamenes_no_validos)}")
        dictamenes_validos = self.env['agenda.entrega.dictamen'].search([('id','not in', dictamenes_no_validos)])
        for record in self:
            record.dictamen_valido_ids = dictamenes_validos.ids

    def _compute_hora_confirmada(self):
        for record in self:
            if record.fecha_confirmada:
                fecha_local = fields.Datetime.context_timestamp(record, record.fecha_confirmada)
                record.hora_confirmada = fecha_local.strftime('%I:%M %p')
            else:
                record.hora_confirmada = False

    def _compute_gerente(self):
        for record in self:
            user_email = record.vehiculo_id.gerente_flota_id.login
            _logger.info("Datos del gerente")
            _logger.info(user_email)
            empleado = self.env['hr.employee'].search([('work_email', '=', user_email)], limit=1)
            _logger.info(empleado)
            if empleado:
                _logger.info("Entra a if")
                record.ejecutivo_id = empleado.id
            else:
                _logger.info("Entra a else")
                record.ejecutivo_id = False


    def _compute_instrumentacion_correcta(self):
        instru_correcta = self.env['agenda.entrega.estatus.instru'].search([('name','=','Correctos')], limit=1)
        comp_correcto1 = self.env['agenda.entrega.estatus.comprobante'].search([('name', '=', 'Validado')], limit=1)
        comp_correcto2 = self.env['agenda.entrega.estatus.comprobante'].search([('name', '=', 'No requiere pago')], limit=1)
        for record in self:
            record.instrumentacion_correcta = False
            if record.etapa_id.name in ['Solicitado','Confirmado']:
                if record.req_instrumentacion.id == instru_correcta.id and record.estatus_comprobante_deposito.id in [comp_correcto1.id, comp_correcto2.id]:
                    record.instrumentacion_correcta = True

    @api.depends('asesor_id')
    def _compute_num_empleado(self):
        for record in self:
            record.num_empleado = record.asesor_id.numero_empleado

    def _compute_color_kanban(self):
        for record in self:
            if record.etapa_id.id == 1:
                record.color_kanban = 1
            elif record.etapa_id.id == 2:
                record.color_kanban = 2
            elif record.etapa_id.id == 3:
                record.color_kanban = 3
            elif record.etapa_id.id == 4:
                record.color_kanban = 4

    def write_custom(self, vals):
        res = super(AgendaEntrega, self).sudo().write(vals)
        return res

    @api.depends('vin_sn','lugar_entrega_id')
    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.id_landing}-{record.dictamen_id.cliente if record.dictamen_id else ''}"

    def _compute_eventos(self):
        etapa_pendiente = self.env['agenda.entrega.estatus.evento'].search([('name','=','Pendiente')], limit=1)
        etapa_atendido = self.env['agenda.entrega.estatus.evento'].search([('name','=','Atendido')], limit=1)
        for record in self:
            pendientes = self.env['agenda.entrega.evento'].search_count([
                ('agenda_id', '=', record.id),
                ('status_id', '=', etapa_pendiente.id)
            ])
            solventados = self.env['agenda.entrega.evento'].search_count([
                ('agenda_id', '=', record.id),
                ('status_id', '=', etapa_atendido.id)
            ])
            record.eventos_pendientes = pendientes
            record.eventos_solventados = solventados

    def crear_evento(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'agenda.entrega.evento.wizard',
            'name': 'Evento',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('fleet_agenda_entrega.evento_view_form').id
        }

    def evidencia(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'evidencia.wizard',
            'name': 'Evidencia',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('fleet_agenda_entrega.evidencia_view_form').id
        }

    def mostrar_eventos(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'agenda.entrega.evento',
            'name': 'Eventos',
            'view_mode': 'list,form',
            'taget': 'new',
            'domain': [('agenda_id', '=', self.id)],
            'context': {'create': False},
        }

    @api.depends('dictamen_id')
    def _compute_datos_vehiculo(self):
        for agenda in self:
            agenda.vehiculo_id = agenda.dictamen_id.vehiculo_id.id
            agenda.modelo_vehiculo_id = agenda.dictamen_id.vehiculo_id.model_id.id
            agenda.version =agenda.dictamen_id.vehiculo_id.version.id
            agenda.vin_sn = agenda.dictamen_id.vehiculo_id.vin_sn
            agenda.condicion_vehiculo_id = agenda.dictamen_id.vehiculo_id.condicion_vehiculo_id.id
            agenda.color = agenda.dictamen_id.vehiculo_id.color
            agenda.year = agenda.dictamen_id.vehiculo_id.model_year
            agenda.producto_id = agenda.dictamen_id.vehiculo_id.producto_id.id
            agenda.plaza_id = agenda.dictamen_id.vehiculo_id.plaza_id.id
            agenda.matricula = agenda.dictamen_id.vehiculo_id.license_plate
            agenda.id_landing = agenda.dictamen_id.landing_id
            agenda.cliente = agenda.dictamen_id.cliente

    @api.depends('dictamen_id')
    def _compute_datos_dictamen(self):
        for record in self:
            dictamen = record.dictamen_id.sudo()
            record.estatus_dictamen = dictamen.status_dictamen.id
            record.email_cliente = dictamen.email_cliente
            record.telefono_cliente = dictamen.telefono_cliente
            record.asesor_id = dictamen.asesor_id.id

    def _compute_mostrar_evento(self):
        for record in self:
            contador = self.env['agenda.entrega.evento'].search_count([('agenda_id', '=', record.id)])
            if contador > 0:
                record.mostrar_evento = True
            else:
                record.mostrar_evento = False