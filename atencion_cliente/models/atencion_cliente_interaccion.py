from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class AtencionClienteInteraccion(models.Model):
    _name = 'atencion.cliente.interaccion'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string="Nombre",
        compute='_compute_name',
    )
    folio = fields.Char(
        string='Folio'
    )
    medio_contacto_id = fields.Many2one(
        comodel_name="atencion.cliente.medio.contacto",
        string="Medio de contacto"
    )
    tipo_solicitud_id = fields.Many2one(
        comodel_name="atencion.cliente.tipo.solicitud",
        string="Tipo de solicitud"
    )
    comentario = fields.Text(
        string="Comentario"
    )
    etapa_id = fields.Many2one(
        comodel_name="atencion.cliente.interaccion.stage",
        string="Etapa",
        default=lambda self: self.env['atencion.cliente.interaccion.stage'].search([('name', '=', 'En proceso')], limit=1)
    )
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
    )
    vehiculo_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehiculo',
        store=True,
        compute='_compute_vehiculo_id',
        inverse='_inverse_vehiculo_id'
    )
    vin_sn = fields.Char(
        string='VIN',
        compute='_compute_datos_vehiculo',
        store=True,
    )
    plaza_id = fields.Many2one(
        comodel_name='fleet.customer.plaza',
        string='Plaza',
        compute='_compute_datos_vehiculo',
        store=True,
    )
    modelo_id = fields.Many2one(
        comodel_name="fleet.vehicle.model",
        compute='_compute_datos_vehiculo',
        store=True
    )
    kilometraje = fields.Float(
        string='Kilometraje',
        compute='_compute_datos_vehiculo',
        store=True
    )
    fecha_asignation = fields.Date(
        string='Fecha de Asignacion'
    )
    poliza_ids = fields.Many2many(
        comodel_name='fleet.poliza',
        compute='_compute_poliza_ids',
        string='Poliza',
    )
    tramite_ids = fields.Many2many(
        comodel_name='fleet.tramite',
        compute='_compute_tramite_ids',
        string='Tramite',
    )
    factura = fields.Binary(
        string='Factura',
        compute='_compute_factura',
    )
    contrato_ids = fields.Many2many(
        comodel_name='fleet.vehicle.log.contract',
        compute='_compute_contrato_ids',
        string='Contrato',
    )
    adaptacion_ids = fields.Many2many(
        comodel_name='fleet.adecuacion',
        compute='_compute_adaptacion_ids',
        string='Adecuación',
    )
    active = fields.Boolean('Active', default=True, tracking=True)
    matricula = fields.Char(
        string="Matricula",
        compute='_compute_datos_vehiculo',
        store=True,
    )
    cie = fields.Char(
        string="Cie",
        store=True,
        compute='_compute_datos_contrato'
    )
    fecha_inicio_arrendamiento = fields.Date(
        string='Inicio de Arrendamiento',
        store=True,
        compute='_compute_datos_contrato'
    )

    @api.depends('vehiculo_id')
    def _compute_datos_contrato(self):
        for record in self:
            if record.vehiculo_id:
                contrato = self.env['fleet.vehicle.log.contract'].search([('vehicle_id','=',record.vehiculo_id.id),('state','=','open')], limit=1)
                if contrato:
                   record.cie = contrato.cie
                   record.fecha_inicio_arrendamiento = contrato.start_date
                else:
                    record.cie = False
                    record.fecha_inicio_arrendamiento = False


    @api.depends('vehiculo_id')
    def _compute_datos_vehiculo(self):
        for record in self:
            if record.vehiculo_id:
                record.vin_sn = record.vehiculo_id.vin_sn if record.vehiculo_id.vin_sn else False
                record.plaza_id = record.vehiculo_id.plaza_id.id if record.vehiculo_id.plaza_id.id else False
                record.modelo_id = record.vehiculo_id.model_id.id if record.vehiculo_id.model_id else False
                record.kilometraje = record.vehiculo_id.odometer if record.vehiculo_id.odometer else False
                record.matricula = record.vehiculo_id.license_plate if record.vehiculo_id.license_plate else False

    @api.depends('vehiculo_id')
    def _compute_poliza_ids(self):
        for record in self:
            if record.vehiculo_id:
                polizas = self.env['fleet.poliza'].search([('vehiculo_id', '=', record.vehiculo_id.id)])
                record.poliza_ids = polizas.ids
            else:
                record.poliza_ids = False

    @api.depends('vehiculo_id')
    def _compute_tramite_ids(self):
        for record in self:
            if record.vehiculo_id:
                tramites = self.env['fleet.tramite'].search([('vehiculo_id', '=', record.vehiculo_id.id)])
                record.tramite_ids = tramites.ids
            else:
                record.tramite_ids = False

    @api.depends('vehiculo_id')
    def _compute_factura(self):
        for record in self:
            if record.vehiculo_id:
                record.factura = record.vehiculo_id.factura_vehiculo
            else:
                record.factura = False

    @api.depends('vehiculo_id')
    def _compute_contrato_ids(self):
        for record in self:
            if record.vehiculo_id:
                contratos = self.env['fleet.vehicle.log.contract'].search([('vehicle_id', '=', record.vehiculo_id.id)])
                record.contrato_ids = contratos.ids
            else:
                record.contrato_ids = False

    @api.depends('vehiculo_id')
    def _compute_adaptacion_ids(self):
        for record in self:
            if record.vehiculo_id:
                adaptaciones = self.env['fleet.adecuacion'].search([('vehiculo_id', '=', record.vehiculo_id.id)])
                record.adaptacion_ids = adaptaciones.ids
            else:
                record.adaptacion_ids = False

    def _inverse_vehiculo_id(self):
        pass

    def return_etapa_renta(self):
        etapa_renta = self.env['fleet.vehicle.state'].search([('es_etapa_rentado', '=', True)], limit=1)
        if etapa_renta:
            return etapa_renta.id
        else:
            return None

    @api.depends('cliente_id')
    def _compute_vehiculo_id(self):
        etapa_renta = self.return_etapa_renta()
        for record in self:
            if record.cliente_id:
                vehiculo = self.env['fleet.vehicle'].search([('driver_id', '=', record.cliente_id.id),('state_id','=', etapa_renta)], limit=1)
                record.vehiculo_id = vehiculo.id if vehiculo else False

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('folio', 'Nuevo') == 'Nuevo':
                vals['folio'] = self.env['ir.sequence'].next_by_code('atencion_compra_seq') or 'AC-0'
        return super().create(vals_list)

    def _compute_name(self):
        for record in self:
            record.name = f"{record.folio}-{record.cliente_id.name}"